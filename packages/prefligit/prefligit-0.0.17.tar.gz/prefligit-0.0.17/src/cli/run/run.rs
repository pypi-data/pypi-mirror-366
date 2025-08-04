use std::cmp::{Reverse, max};
use std::collections::{HashMap, HashSet};
use std::fmt::Write as _;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::rc::Rc;

use anstream::ColorChoice;
use anyhow::{Context, Result};
use futures::StreamExt;
use futures::stream::FuturesUnordered;
use indoc::indoc;
use owo_colors::{OwoColorize, Style};
use rand::SeedableRng;
use rand::prelude::{SliceRandom, StdRng};
use tokio::io::AsyncWriteExt;
use tracing::{debug, trace};
use unicode_width::UnicodeWidthStr;

use constants::env_vars::EnvVars;

use crate::cli::reporter::{HookInitReporter, HookInstallReporter};
use crate::cli::run::keeper::WorkTreeKeeper;
use crate::cli::run::{CollectOptions, FileFilter, collect_files};
use crate::cli::{ExitStatus, RunExtraArgs};
use crate::config::{Language, Stage};
use crate::fs::Simplified;
use crate::git;
use crate::hook::{Hook, InstalledHook, Project};
use crate::printer::Printer;
use crate::store::Store;

enum HookToRun {
    Skipped(Box<Hook>),
    ToRun(Box<InstalledHook>),
}

#[allow(clippy::too_many_arguments)]
pub(crate) async fn run(
    config: Option<PathBuf>,
    hook_id: Option<String>,
    hook_stage: Option<Stage>,
    from_ref: Option<String>,
    to_ref: Option<String>,
    all_files: bool,
    files: Vec<PathBuf>,
    show_diff_on_failure: bool,
    extra_args: RunExtraArgs,
    verbose: bool,
    printer: Printer,
) -> Result<ExitStatus> {
    // Prevent recursive post-checkout hooks.
    if matches!(hook_stage, Some(Stage::PostCheckout))
        && EnvVars::is_set(EnvVars::PREFLIGIT_INTERNAL__SKIP_POST_CHECKOUT)
    {
        return Ok(ExitStatus::Success);
    }

    let should_stash = !all_files && files.is_empty();

    // Check if we have unresolved merge conflict files and fail fast.
    if should_stash && git::has_unmerged_paths().await? {
        writeln!(
            printer.stderr(),
            "You have unmerged paths. Resolve them before running prefligit."
        )?;
        return Ok(ExitStatus::Failure);
    }

    let config_file = Project::find_config_file(config)?;
    if should_stash && file_not_staged(&config_file).await? {
        writeln!(
            printer.stderr(),
            indoc!(
                "Your prefligit configuration file is not staged.
                Run `git add {}` to fix this."
            ),
            &config_file.user_display()
        )?;
        return Ok(ExitStatus::Failure);
    }

    // Set env vars for hooks.
    let env_vars = fill_envs(from_ref.as_ref(), to_ref.as_ref(), &extra_args);

    let mut project = Project::new(config_file)?;
    let store = Store::from_settings()?.init()?;

    let reporter = HookInitReporter::from(printer);

    let lock = store.lock_async().await?;
    let hooks = project.init_hooks(&store, Some(&reporter)).await?;

    let hooks: Vec<_> = hooks
        .into_iter()
        .filter(|h| {
            hook_id
                .as_deref()
                .is_none_or(|hook_id| h.id == hook_id || h.alias == hook_id)
        })
        .filter(|h| hook_stage.is_none_or(|stage| h.stages.contains(&stage)))
        .collect();

    if hooks.is_empty() && hook_id.is_some() {
        if let Some(hook_stage) = hook_stage {
            writeln!(
                printer.stderr(),
                "No hook found for id `{}` and stage `{}`",
                hook_id.unwrap().cyan(),
                hook_stage.cyan()
            )?;
        } else {
            writeln!(
                printer.stderr(),
                "No hook found for id `{}`",
                hook_id.unwrap().cyan()
            )?;
        }
        return Ok(ExitStatus::Failure);
    }

    let skips = get_skips();
    let skips = hooks
        .iter()
        .filter(|h| skips.contains(&h.id) || skips.contains(&h.alias))
        .map(|h| h.idx)
        .collect::<HashSet<_>>();
    let to_run = hooks
        .iter()
        .filter(|h| !skips.contains(&h.idx))
        .cloned()
        .collect::<Vec<_>>();

    debug!(
        "Hooks going to run: {:?}",
        to_run.iter().map(|h| &h.id).collect::<Vec<_>>()
    );
    let reporter = HookInstallReporter::from(printer);
    let mut installed_hooks = install_hooks(&to_run, &store, &reporter).await?;
    drop(lock);

    let hooks = hooks
        .into_iter()
        .map(|h| {
            if skips.contains(&h.idx) {
                HookToRun::Skipped(Box::new(h))
            } else {
                // Find and remove the matching resolved hook
                let resolved_idx = installed_hooks
                    .iter()
                    .position(|r| r.idx == h.idx)
                    .expect("Resolved hook must exist");
                HookToRun::ToRun(Box::new(installed_hooks.swap_remove(resolved_idx)))
            }
        })
        .collect::<Vec<_>>();

    // Clear any unstaged changes from the git working directory.
    let mut _guard = None;
    if should_stash {
        _guard = Some(WorkTreeKeeper::clean(&store).await?);
    }

    let filenames = collect_files(CollectOptions {
        hook_stage,
        from_ref,
        to_ref,
        all_files,
        files,
        commit_msg_filename: extra_args.commit_msg_filename.clone(),
    })
    .await?;

    let filter = FileFilter::new(
        &filenames,
        project.config().files.as_deref(),
        project.config().exclude.as_deref(),
    )?;
    trace!("Files after filtered: {}", filter.len());

    run_hooks(
        &hooks,
        &filter,
        env_vars,
        &store,
        project.config().fail_fast.unwrap_or(false),
        show_diff_on_failure,
        verbose,
        printer,
    )
    .await
}

async fn file_not_staged(file: &Path) -> Result<bool> {
    let status = git::git_cmd("git diff")?
        .arg("diff")
        .arg("--quiet") // Implies --exit-code
        .arg("--no-ext-diff")
        .arg(file)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .check(false)
        .status()
        .await?;

    Ok(status.code().is_some_and(|code| code == 1))
}

fn fill_envs(
    from_ref: Option<&String>,
    to_ref: Option<&String>,
    args: &RunExtraArgs,
) -> HashMap<&'static str, String> {
    // TODO: how to change these env vars?
    let mut env = HashMap::new();
    env.insert("PRE_COMMIT", "1".into());

    if let Some(ref source) = args.prepare_commit_message_source {
        env.insert("PRE_COMMIT_COMMIT_MSG_SOURCE", source.clone());
    }
    if let Some(ref object) = args.commit_object_name {
        env.insert("PRE_COMMIT_COMMIT_OBJECT_NAME", object.clone());
    }
    if let Some(from_ref) = from_ref {
        env.insert("PRE_COMMIT_ORIGIN", from_ref.clone());
        env.insert("PRE_COMMIT_FROM_REF", from_ref.clone());
    }
    if let Some(to_ref) = to_ref {
        env.insert("PRE_COMMIT_SOURCE", to_ref.clone());
        env.insert("PRE_COMMIT_TO_REF", to_ref.clone());
    }
    if let Some(ref upstream) = args.pre_rebase_upstream {
        env.insert("PRE_COMMIT_PRE_REBASE_UPSTREAM", upstream.clone());
    }
    if let Some(ref branch) = args.pre_rebase_branch {
        env.insert("PRE_COMMIT_PRE_REBASE_BRANCH", branch.clone());
    }
    if let Some(ref branch) = args.local_branch {
        env.insert("PRE_COMMIT_LOCAL_BRANCH", branch.clone());
    }
    if let Some(ref branch) = args.remote_branch {
        env.insert("PRE_COMMIT_REMOTE_BRANCH", branch.clone());
    }
    if let Some(ref name) = args.remote_name {
        env.insert("PRE_COMMIT_REMOTE_NAME", name.clone());
    }
    if let Some(ref url) = args.remote_url {
        env.insert("PRE_COMMIT_REMOTE_URL", url.clone());
    }
    if let Some(ref checkout) = args.checkout_type {
        env.insert("PRE_COMMIT_CHECKOUT_TYPE", checkout.clone());
    }
    if args.is_squash_merge {
        env.insert("PRE_COMMIT_SQUASH_MERGE", "1".into());
    }
    if let Some(ref command) = args.rewrite_command {
        env.insert("PRE_COMMIT_REWRITE_COMMAND", command.clone());
    }

    env
}

fn get_skips() -> Vec<String> {
    match EnvVars::var_os(EnvVars::SKIP) {
        Some(s) if !s.is_empty() => s
            .to_string_lossy()
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect(),
        _ => vec![],
    }
}

pub async fn install_hooks(
    hooks: &[Hook],
    store: &Store,
    reporter: &HookInstallReporter,
) -> Result<Vec<InstalledHook>> {
    let mut new_installed = Vec::with_capacity(hooks.len());
    let mut group_futures = FuturesUnordered::new();
    // TODO: how to eliminate the Rc?
    let installed_hooks = Rc::new(store.installed_hooks().collect::<Vec<_>>());

    let mut hooks_by_language = HashMap::new();
    for hook in hooks {
        hooks_by_language
            .entry(hook.language)
            .or_insert_with(Vec::new)
            .push(hook.clone());
    }

    // Group hooks by language to enable parallel installation across different languages.
    // Within each language group, hooks are installed sequentially, allowing later hooks
    // to leverage the environment or tools installed by previous ones.
    for (_, mut hooks) in hooks_by_language {
        let installed_hooks = installed_hooks.clone();
        // Install hooks from the most dependent to the least dependent,
        // the later hooks can use the environment of the earlier ones.
        hooks.sort_unstable_by_key(|h| Reverse(h.dependencies().len()));

        group_futures.push(async move {
            let mut hook_envs = Vec::with_capacity(hooks.len());
            let mut newly_installed = Vec::new();
            // Process hooks sequentially within each language group
            for hook in &hooks {
                // Find a matching installed hook environment.
                if let Some(info) = installed_hooks
                    .iter()
                    .chain(&newly_installed)
                    .find(|info| info.matches(hook))
                {
                    debug!(
                        "Found installed environment for hook `{hook}` at `{}`",
                        info.env_path.display()
                    );
                    hook_envs.push(InstalledHook::Installed {
                        hook: Box::new(hook.clone()),
                        info: Box::new(info.clone()),
                    });
                    continue;
                }

                debug!("No matching environment found for hook `{hook}`, installing...");

                let progress = reporter.on_install_start(hook);

                let installed_hook = hook
                    .language
                    .install(hook, store)
                    .await
                    .context(format!("Failed to install hook `{hook}`"))?;

                installed_hook
                    .mark_as_installed(store)
                    .await
                    .context(format!("Failed to mark hook `{hook}` as installed"))?;

                if let InstalledHook::Installed { info, .. } = &installed_hook {
                    newly_installed.push(*info.clone());
                }
                hook_envs.push(installed_hook);

                reporter.on_install_complete(progress);
            }
            anyhow::Ok(hook_envs)
        });
    }

    while let Some(result) = group_futures.next().await {
        new_installed.extend(result?);
    }
    reporter.on_complete();

    Ok(new_installed)
}

const PASSED: &str = "Passed";
const FAILED: &str = "Failed";
const SKIPPED: &str = "Skipped";
const NO_FILES: &str = "(no files to check)";
const UNIMPLEMENTED: &str = "(unimplemented yet)";

fn status_line(start: &str, cols: usize, end_msg: &str, end_color: Style, postfix: &str) -> String {
    let dots = cols - start.width_cjk() - end_msg.len() - postfix.len() - 1;
    format!(
        "{}{}{}{}",
        start,
        ".".repeat(dots),
        postfix,
        end_msg.style(end_color)
    )
}

fn calculate_columns(hooks: &[HookToRun]) -> usize {
    let name_len = hooks
        .iter()
        .filter_map(|hook| {
            if let HookToRun::ToRun(hook) = hook {
                Some(hook.name.width_cjk())
            } else {
                None
            }
        })
        .max()
        .unwrap_or(0);
    max(80, name_len + 3 + NO_FILES.len() + 1 + SKIPPED.len())
}

/// Run all hooks.
async fn run_hooks(
    hooks: &[HookToRun],
    filter: &FileFilter<'_>,
    env_vars: HashMap<&'static str, String>,
    store: &Store,
    fail_fast: bool,
    show_diff_on_failure: bool,
    verbose: bool,
    printer: Printer,
) -> Result<ExitStatus> {
    let columns = calculate_columns(hooks);
    let mut success = true;

    let mut diff = git::get_diff().await?;
    // Hooks might modify the files, so they must be run sequentially.
    for hook in hooks {
        let (hook_success, new_diff) = run_hook(
            hook, filter, &env_vars, store, diff, columns, verbose, printer,
        )
        .await?;

        success &= hook_success;
        diff = new_diff;
        let fail_fast = fail_fast
            || match hook {
                HookToRun::Skipped(_) => false,
                HookToRun::ToRun(hook) => hook.fail_fast,
            };
        if !success && fail_fast {
            break;
        }
    }

    if !success && show_diff_on_failure {
        writeln!(printer.stdout(), "All changes made by hooks:")?;
        let color = match ColorChoice::global() {
            ColorChoice::Auto => "--color=auto",
            ColorChoice::Always | ColorChoice::AlwaysAnsi => "--color=always",
            ColorChoice::Never => "--color=never",
        };
        git::git_cmd("git diff")?
            .arg("--no-pager")
            .arg("diff")
            .arg("--no-ext-diff")
            .arg(color)
            .check(true)
            .spawn()?
            .wait()
            .await?;
    }

    if success {
        Ok(ExitStatus::Success)
    } else {
        Ok(ExitStatus::Failure)
    }
}

/// Shuffle the files so that they more evenly fill out the xargs
/// partitions, but do it deterministically in case a hook cares about ordering.
fn shuffle<T>(filenames: &mut [T]) {
    const SEED: u64 = 1_542_676_187;
    let mut rng = StdRng::seed_from_u64(SEED);
    filenames.shuffle(&mut rng);
}

async fn run_hook(
    hook: &HookToRun,
    filter: &FileFilter<'_>,
    env_vars: &HashMap<&'static str, String>,
    store: &Store,
    diff: Vec<u8>,
    columns: usize,
    verbose: bool,
    printer: Printer,
) -> Result<(bool, Vec<u8>)> {
    let hook = match hook {
        HookToRun::Skipped(hook) => {
            writeln!(
                printer.stdout(),
                "{}",
                status_line(
                    &hook.name,
                    columns,
                    SKIPPED,
                    Style::new().black().on_yellow(),
                    "",
                )
            )?;
            return Ok((true, diff));
        }
        HookToRun::ToRun(hook) => hook,
    };

    let mut filenames = filter.for_hook(hook)?;

    if filenames.is_empty() && !hook.always_run {
        writeln!(
            printer.stdout(),
            "{}",
            status_line(
                &hook.name,
                columns,
                SKIPPED,
                Style::new().black().on_cyan(),
                NO_FILES,
            )
        )?;
        return Ok((true, diff));
    }

    if !Language::supported(hook.language) {
        writeln!(
            printer.stdout(),
            "{}",
            status_line(
                &hook.name,
                columns,
                SKIPPED,
                Style::new().black().on_cyan(),
                UNIMPLEMENTED,
            )
        )?;
        return Ok((true, diff));
    }

    write!(
        printer.stdout(),
        "{}{}",
        &hook.name,
        ".".repeat(columns - hook.name.width_cjk() - PASSED.len() - 1)
    )?;
    std::io::stdout().flush()?;

    let start = std::time::Instant::now();

    let filenames = if hook.pass_filenames {
        shuffle(&mut filenames);
        filenames
    } else {
        vec![]
    };

    let (status, output) = hook
        .language
        .run(hook, &filenames, env_vars, store)
        .await
        .context(format!("Failed to run hook `{hook}`"))?;

    let duration = start.elapsed();

    let new_diff = git::get_diff().await?;
    let file_modified = diff != new_diff;
    let success = status == 0 && !file_modified;
    if success {
        writeln!(printer.stdout(), "{}", PASSED.on_green())?;
    } else {
        writeln!(printer.stdout(), "{}", FAILED.on_red())?;
    }

    if verbose || hook.verbose || !success {
        writeln!(
            printer.stdout(),
            "{}",
            format!("- hook id: {}", hook.id).dimmed()
        )?;
        if verbose || hook.verbose {
            writeln!(
                printer.stdout(),
                "{}",
                format!("- duration: {:.2?}s", duration.as_secs_f64()).dimmed()
            )?;
        }
        if status != 0 {
            writeln!(
                printer.stdout(),
                "{}",
                format!("- exit code: {status}").dimmed()
            )?;
        }
        if file_modified {
            writeln!(
                printer.stdout(),
                "{}",
                "- files were modified by this hook".dimmed()
            )?;
        }

        // To be consistent with pre-commit, merge stderr into stdout.
        let stdout = output.trim_ascii();
        if !stdout.is_empty() {
            if let Some(file) = hook.log_file.as_deref() {
                let mut file = fs_err::tokio::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(file)
                    .await?;
                file.write_all(stdout).await?;
                file.sync_all().await?;
            } else {
                writeln!(
                    printer.stdout(),
                    "{}",
                    textwrap::indent(&String::from_utf8_lossy(stdout), "  ").dimmed()
                )?;
            }
        }
    }

    Ok((success, new_diff))
}
