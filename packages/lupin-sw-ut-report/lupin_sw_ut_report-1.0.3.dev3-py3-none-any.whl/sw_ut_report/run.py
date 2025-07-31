import os
import sys
from os import PathLike
from typing import Dict, List, Optional

import typer

from sw_ut_report.__init__ import __version__
from sw_ut_report.parse_txt_file import format_txt_file
from sw_ut_report.parse_xml_file import format_xml_to_dict
from sw_ut_report.template_manager import get_local_template
from sw_ut_report.push_ut_test_results import push_ut_test_results_to_jama, validate_jama_environment_for_ut_push

cli = typer.Typer()


def input_folder_option() -> typer.Option:
    return typer.Option(
        ...,
        "--input-folder",
        help="Path to the folder containing the txt and xml files",
    )


def version_callback(value: bool):
    if value:
        typer.echo(__version__)
        sys.exit(0)


@cli.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
    input_folder: str = input_folder_option(),
    generate_markdown: bool = typer.Option(True, "--markdown/--no-markdown", help="Generate markdown report"),
    create_jama_ut: bool = typer.Option(False, "--create-ut", help="Create/update unit tests in Jama"),
    module_name: Optional[str] = typer.Option(None, "--module-name", help="Module name for Jama UT creation (required with --create-ut)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes to Jama"),
    push_ut_test_results: Optional[str] = typer.Option(None, "--push-ut-test-results", help="Push UT test results to Jama for the specified version"),
):
    if ctx.invoked_subcommand is None:
        generate_report(input_folder, generate_markdown, create_jama_ut, module_name, dry_run, push_ut_test_results)


@cli.command()
def generate_report(
    input_folder: str = input_folder_option(),
    generate_markdown: bool = typer.Option(True, "--markdown/--no-markdown", help="Generate markdown report"),
    create_jama_ut: bool = typer.Option(False, "--create-ut", help="Create/update unit tests in Jama"),
    module_name: Optional[str] = typer.Option(None, "--module-name", help="Module name for Jama UT creation (required with --create-ut)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done without making changes to Jama"),
    push_ut_test_results: Optional[str] = typer.Option(None, "--push-ut-test-results", help="Push UT test results to Jama for the specified version"),
):
    # Validate parameters
    if create_jama_ut and not module_name:
        typer.echo("Error: --module-name is required when --create-ut is used", err=True)
        sys.exit(1)

    if push_ut_test_results and not input_folder:
        typer.echo("Error: --input-folder is required when --push-ut-test-results is used", err=True)
        sys.exit(1)

    if not generate_markdown and not create_jama_ut and not push_ut_test_results:
        typer.echo("Error: At least one output option must be specified (--markdown, --create-ut, or --push-ut-test-results)", err=True)
        sys.exit(1)

    # Dry-run validation
    if dry_run and not create_jama_ut:
        typer.echo("Note: --dry-run only applies to Jama operations. Use with --create-ut to see Jama actions.")

    # Handle push UT test results first
    if push_ut_test_results:
        typer.echo(f"Pushing UT test results to Jama for version: {push_ut_test_results}")

        try:
            from sw_ut_report.jama_common import setup_logging, JamaConnectionError, JamaValidationError
            setup_logging()

            ut_result = push_ut_test_results_to_jama(push_ut_test_results, input_folder)

            if ut_result == 0:
                typer.echo("✅ Successfully pushed UT test results to Jama")
                typer.echo(f"Exit code: {ut_result}")
                sys.exit(0)
            elif ut_result == 1:
                typer.echo("❌ Failed to push UT test results to Jama", err=True)
                typer.echo(f"Exit code: {ut_result}")
                sys.exit(1)
            elif ut_result == 2:
                typer.echo("⚠️ Pushed UT test results to Jama with warnings")
                typer.echo(f"Exit code: {ut_result}")
                sys.exit(2)
            else:
                typer.echo("❌ Failed to push UT test results to Jama", err=True)
                typer.echo(f"Exit code: 1 (unknown result: {ut_result})")
                sys.exit(1)

        except (JamaConnectionError, JamaValidationError) as e:
            typer.echo(f"❌ Jama operation failed: {e}", err=True)
            typer.echo("Exit code: 1")
            sys.exit(1)
        except Exception as e:
            typer.echo(f"❌ Error pushing UT test results: {e}", err=True)
            typer.echo("Exit code: 1")
            sys.exit(1)
        return

    typer.echo("test reports generation started")

    all_reports = []

    try:
        file_list = os.listdir(input_folder)
    except FileNotFoundError:
        typer.echo(f"Path '{input_folder}' does not exist.")
        sys.exit(1)
    except PermissionError:
        typer.echo(f"Permission denied for the folder '{input_folder}'.")
        sys.exit(1)

    for filename in file_list:
        input_file = os.path.join(input_folder, filename)
        _, file_extension = os.path.splitext(filename)

        match file_extension.lower():
            case ".txt":
                scenarios = format_txt_file(read_file_content(input_file))
                for scenario in scenarios:
                    scenario["filename"] = filename
                all_reports.append(
                    {"type": "txt", "filename": filename, "content": scenarios}
                )

            case ".xml":
                suites_data = format_xml_to_dict(input_file)
                suites_data["filename"] = filename
                all_reports.append(
                    {"type": "xml", "filename": filename, "content": suites_data}
                )

            case _:
                if os.path.isdir(input_file):
                    typer.echo(f"Skipping folder: {filename}")
                    continue
                else:
                    print(f"Skipping unsupported file format: {filename}")
                    continue

    if not all_reports:
        typer.echo("No test files found to process.")
        return

    # Execute requested operations
    exit_code = 0  # Default success code

    # Create UTs in Jama if requested
    if create_jama_ut:
        try:
            if dry_run:
                from sw_ut_report.jama_ut_manager import dry_run_unit_tests_creation
                from sw_ut_report.jama_common import JamaConnectionError, JamaValidationError, setup_logging

                # Setup logging for Jama operations
                setup_logging()

                typer.echo(f"DRY-RUN: Analyzing what would be done for module: {module_name}")
                typer.echo("=" * 60)

                ut_result = dry_run_unit_tests_creation(module_name, all_reports)

                if ut_result == 0:
                    typer.echo("✅ Dry-run analysis completed successfully")
                    exit_code = 0
                elif ut_result == 1:
                    typer.echo("❌ Dry-run analysis found errors", err=True)
                    exit_code = 1
                elif ut_result == 2:
                    typer.echo("⚠️ Dry-run analysis completed with warnings")
                    exit_code = 2
                else:
                    typer.echo("❌ Dry-run analysis failed", err=True)
                    exit_code = 1

            else:
                from sw_ut_report.jama_ut_manager import create_unit_tests_in_jama
                from sw_ut_report.jama_common import JamaConnectionError, JamaValidationError, setup_logging

                # Setup logging for Jama operations
                setup_logging()

                typer.echo(f"Creating/updating unit tests in Jama for module: {module_name}")
                typer.echo("=" * 60)

                ut_result = create_unit_tests_in_jama(module_name, all_reports)

                if ut_result == 0:
                    typer.echo("✅ Successfully created/updated unit tests in Jama")
                    exit_code = 0
                elif ut_result == 1:
                    typer.echo("❌ Failed to create/update unit tests in Jama", err=True)
                    exit_code = 1
                elif ut_result == 2:
                    typer.echo("⚠️ Created/updated unit tests in Jama with warnings")
                    exit_code = 2
                else:
                    typer.echo("❌ Failed to create/update unit tests in Jama", err=True)
                    exit_code = 1

        except (JamaConnectionError, JamaValidationError) as e:
            typer.echo(f"❌ Jama operation failed: {e}", err=True)
            exit_code = 1
        except Exception as e:
            typer.echo(f"❌ Unexpected error during Jama operations: {e}", err=True)
            exit_code = 1

        # Exit with the appropriate code for Jama operations
        typer.echo(f"Exit code: {exit_code}")
        sys.exit(exit_code)

    # Generate markdown report if requested
    if generate_markdown:
        try:
            generate_single_markdown(all_reports)
            typer.echo("✅ Successfully generated markdown report")
            # Keep exit_code as 0 for success
        except Exception as e:
            typer.echo(f"❌ Failed to generate markdown report: {e}", err=True)
            exit_code = 1

    # Final exit with the determined code
    typer.echo(f"Final exit code: {exit_code}")
    sys.exit(exit_code)


def read_file_content(input_file: PathLike) -> str:
    with open(input_file, "r", encoding="utf-8") as f:
        return f.read()


def generate_single_markdown(all_reports: List[Dict]) -> None:
    template = get_local_template("combined_test_report.j2")
    markdown_content = template.render(reports=all_reports)

    with open("sw_ut_report.md", "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)
