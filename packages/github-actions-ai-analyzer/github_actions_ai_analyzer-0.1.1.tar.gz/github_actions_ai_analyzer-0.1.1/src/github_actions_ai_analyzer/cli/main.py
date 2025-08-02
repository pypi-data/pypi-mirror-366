"""
CLI メインエントリーポイント

GitHub Actions AI Analyzerのコマンドラインインターフェースのメイン関数です。
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..core.analyzer import GitHubActionsAnalyzer
from ..types import LogLevel

console = Console()


@click.group()
@click.version_option(version="0.1.1")
def main():
    """GitHub Actions AI Analyzer - エラーログ解析ツール"""
    pass


@main.command()
@click.argument("log_file", type=click.Path(exists=True))
@click.option(
    "--workflow",
    "-w",
    type=click.Path(exists=True),
    help="ワークフローファイルのパス",
)
@click.option(
    "--repository", "-r", type=click.Path(exists=True), help="リポジトリのパス"
)
@click.option(
    "--min-level",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error", "fatal"]),
    default="warning",
    help="最小ログレベル",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
    help="出力形式",
)
def analyze(log_file, workflow, repository, min_level, output):
    """ログファイルを解析してエラー分析を実行"""
    try:
        console.print("[bold blue]GitHub Actions AI Analyzer[/bold blue]")
        console.print(f"ログファイル: {log_file}")

        # ログレベルを変換
        valid_levels = [level.value for level in LogLevel]
        if min_level in valid_levels:
            log_level = LogLevel(min_level)
        else:
            log_level = LogLevel.WARNING

        # アナライザーを作成
        analyzer = GitHubActionsAnalyzer()

        # 解析実行
        with console.status("[bold green]解析中..."):
            result = analyzer.analyze_log_file(
                log_file_path=log_file,
                workflow_file_path=workflow,
                repository_path=repository,
                min_log_level=log_level,
            )

        # 結果を表示
        _display_analysis_result(result, output)

    except Exception as e:
        console.print(f"[bold red]エラー: {e}[/bold red]")
        raise click.Abort()


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True))
def validate(workflow_file):
    """ワークフローファイルを検証"""
    console.print("[bold blue]ワークフローファイル検証[/bold blue]")
    console.print(f"ファイル: {workflow_file}")

    # TODO: ワークフロー検証機能を実装
    console.print("[yellow]ワークフロー検証機能は未実装です[/yellow]")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--interval", "-i", type=int, default=30, help="監視間隔（秒）")
def watch(directory, interval):
    """ディレクトリを監視してログファイルの変更を自動解析"""
    console.print("[bold blue]ログファイル監視[/bold blue]")
    console.print(f"ディレクトリ: {directory}")
    console.print(f"監視間隔: {interval}秒")

    # TODO: ファイル監視機能を実装
    console.print("[yellow]ファイル監視機能は未実装です[/yellow]")


def _display_analysis_result(result, output_format: str):
    """解析結果を表示"""
    if output_format == "text":
        _display_text_result(result)
    elif output_format == "json":
        _display_json_result(result)
    elif output_format == "yaml":
        _display_yaml_result(result)


def _display_text_result(result):
    """テキスト形式で結果を表示"""
    # サマリー
    summary_panel = Panel(
        Text(result.summary, style="bold green"),
        title="解析サマリー",
        border_style="green",
    )
    console.print(summary_panel)

    # エラー分析
    if result.error_analyses:
        error_table = Table(title="エラー分析結果")
        error_table.add_column("ID", style="cyan")
        error_table.add_column("根本原因", style="red")
        error_table.add_column("重要度", style="yellow")
        error_table.add_column("影響ステップ", style="blue")

        for analysis in result.error_analyses:
            error_table.add_row(
                analysis.error_id,
                analysis.root_cause,
                analysis.severity,
                (
                    ", ".join(analysis.affected_steps)
                    if analysis.affected_steps
                    else "なし"
                ),
            )

        console.print(error_table)

    # 解決策提案
    if result.solution_proposals:
        solution_table = Table(title="解決策提案")
        solution_table.add_column("タイトル", style="cyan")
        solution_table.add_column("説明", style="white")
        solution_table.add_column("信頼度", style="green")
        solution_table.add_column("推定時間", style="yellow")

        for solution in result.solution_proposals:
            solution_table.add_row(
                solution.title,
                solution.description,
                f"{solution.confidence:.1%}",
                solution.estimated_time or "不明",
            )

        console.print(solution_table)

    # 推奨事項
    if result.recommendations:
        recommendations_panel = Panel(
            "\n".join([f"• {rec}" for rec in result.recommendations]),
            title="推奨事項",
            border_style="blue",
        )
        console.print(recommendations_panel)


def _display_json_result(result):
    """JSON形式で結果を表示"""
    import json

    console.print(
        json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
    )


def _display_yaml_result(result):
    """YAML形式で結果を表示"""
    import yaml

    console.print(
        yaml.dump(
            result.model_dump(), default_flow_style=False, allow_unicode=True
        )
    )


if __name__ == "__main__":
    main()
