"""Narrative report generation in Markdown format."""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set
from io import StringIO


class NarrativeReportGenerator:
    """Generate human-readable narrative reports in Markdown."""
    
    def __init__(self) -> None:
        """Initialize narrative report generator."""
        self.templates = {
            'high_performer': "{name} led development with {commits} commits ({pct}% of total activity)",
            'multi_project': "{name} worked across {count} projects, primarily on {primary} ({primary_pct}%)",
            'focused_developer': "{name} showed strong focus on {project} with {pct}% of their time",
            'ticket_coverage': "The team maintained {coverage}% ticket coverage, indicating {quality} process adherence",
            'work_distribution': "Work distribution shows a {distribution} pattern with a Gini coefficient of {gini}"
        }
    
    def generate_narrative_report(self, 
                                commits: List[Dict[str, Any]],
                                prs: List[Dict[str, Any]],
                                developer_stats: List[Dict[str, Any]],
                                activity_dist: List[Dict[str, Any]],
                                focus_data: List[Dict[str, Any]],
                                insights: List[Dict[str, Any]],
                                ticket_analysis: Dict[str, Any],
                                pr_metrics: Dict[str, Any],
                                output_path: Path,
                                weeks: int) -> Path:
        """Generate comprehensive narrative report."""
        report = StringIO()
        
        # Header
        report.write("# GitFlow Analytics Report\n\n")
        report.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"**Analysis Period**: Last {weeks} weeks\n\n")
        
        # Executive Summary
        report.write("## Executive Summary\n\n")
        self._write_executive_summary(report, commits, developer_stats, ticket_analysis)
        
        # Team Composition
        report.write("\n## Team Composition\n\n")
        self._write_team_composition(report, developer_stats, focus_data)
        
        # Project Activity
        report.write("\n## Project Activity\n\n")
        self._write_project_activity(report, activity_dist, commits)
        
        # Development Patterns
        report.write("\n## Development Patterns\n\n")
        self._write_development_patterns(report, insights, focus_data)
        
        # Pull Request Analysis (if available)
        if pr_metrics and pr_metrics.get('total_prs', 0) > 0:
            report.write("\n## Pull Request Analysis\n\n")
            self._write_pr_analysis(report, pr_metrics, prs)
        
        # Ticket Tracking
        report.write("\n## Issue Tracking\n\n")
        self._write_ticket_tracking(report, ticket_analysis)
        
        # Recommendations
        report.write("\n## Recommendations\n\n")
        self._write_recommendations(report, insights, ticket_analysis, focus_data)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(report.getvalue())
        
        return output_path
    
    def _write_executive_summary(self, report: StringIO, commits: List[Dict[str, Any]], 
                               developer_stats: List[Dict[str, Any]], 
                               ticket_analysis: Dict[str, Any]) -> None:
        """Write executive summary section."""
        total_commits = len(commits)
        total_developers = len(developer_stats)
        total_lines = sum(
            c.get('filtered_insertions', c.get('insertions', 0)) + 
            c.get('filtered_deletions', c.get('deletions', 0)) 
            for c in commits
        )
        
        report.write(f"- **Total Commits**: {total_commits:,}\n")
        report.write(f"- **Active Developers**: {total_developers}\n")
        report.write(f"- **Lines Changed**: {total_lines:,}\n")
        report.write(f"- **Ticket Coverage**: {ticket_analysis['commit_coverage_pct']:.1f}%\n")
        
        # Projects worked on
        projects = set(c.get('project_key', 'UNKNOWN') for c in commits)
        report.write(f"- **Active Projects**: {len(projects)} ({', '.join(sorted(projects))})\n")
        
        # Top contributor
        if developer_stats:
            top_dev = developer_stats[0]
            report.write(f"- **Top Contributor**: {top_dev['primary_name']} ")
            report.write(f"({top_dev['total_commits']} commits)\n")
    
    def _write_team_composition(self, report: StringIO, developer_stats: List[Dict[str, Any]], 
                              focus_data: List[Dict[str, Any]]) -> None:
        """Write team composition analysis."""
        report.write("### Developer Profiles\n\n")
        
        # Create developer lookup for focus data
        focus_lookup = {d['developer']: d for d in focus_data}
        
        for dev in developer_stats[:10]:  # Top 10 developers
            name = dev['primary_name']
            commits = dev['total_commits']
            
            report.write(f"**{name}**\n")
            report.write(f"- Commits: {commits}\n")
            
            # Add focus data if available
            if name in focus_lookup:
                focus = focus_lookup[name]
                report.write(f"- Primary Project: {focus['primary_project']} ")
                report.write(f"({focus['primary_project_pct']:.1f}% of time)\n")
                report.write(f"- Work Style: {focus['work_style']}\n")
                report.write(f"- Active Pattern: {focus['time_pattern']}\n")
            
            report.write("\n")
    
    def _write_project_activity(self, report: StringIO, activity_dist: List[Dict[str, Any]], 
                              commits: List[Dict[str, Any]]) -> None:
        """Write project activity breakdown."""
        # Aggregate by project
        project_totals: Dict[str, Dict[str, Any]] = {}
        for row in activity_dist:
            project = row['project']
            if project not in project_totals:
                project_totals[project] = {
                    'commits': 0,
                    'lines': 0,
                    'developers': set()
                }
            data = project_totals[project]
            data['commits'] += row['commits']
            data['lines'] += row['lines_changed']
            developers_set: Set[str] = data['developers']
            developers_set.add(row['developer'])
        
        # Sort by commits
        sorted_projects = sorted(project_totals.items(), 
                               key=lambda x: x[1]['commits'], reverse=True)
        
        report.write("### Activity by Project\n\n")
        for project, data in sorted_projects:
            report.write(f"**{project}**\n")
            report.write(f"- Commits: {data['commits']} ")
            report.write(f"({data['commits'] / len(commits) * 100:.1f}% of total)\n")
            report.write(f"- Lines Changed: {data['lines']:,}\n")
            report.write(f"- Active Developers: {len(data['developers'])}\n\n")
    
    def _write_development_patterns(self, report: StringIO, insights: List[Dict[str, Any]], 
                                  focus_data: List[Dict[str, Any]]) -> None:
        """Write development patterns analysis."""
        report.write("### Key Patterns Identified\n\n")
        
        # Group insights by category
        by_category: Dict[str, List[Dict[str, Any]]] = {}
        for insight in insights:
            category = insight['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(insight)
        
        for category, category_insights in by_category.items():
            report.write(f"**{category}**:\n")
            for insight in category_insights:
                report.write(f"- {insight['insight']}: {insight['value']} ")
                report.write(f"({insight['impact']})\n")
            report.write("\n")
        
        # Add focus insights
        if focus_data:
            avg_focus = sum(d['focus_score'] for d in focus_data) / len(focus_data)
            report.write(f"**Developer Focus**: Average focus score of {avg_focus:.1f}% ")
            
            if avg_focus > 80:
                report.write("indicates strong project concentration\n")
            elif avg_focus > 60:
                report.write("shows moderate multi-project work\n")
            else:
                report.write("suggests high context switching\n")
    
    def _write_pr_analysis(self, report: StringIO, pr_metrics: Dict[str, Any], 
                         prs: List[Dict[str, Any]]) -> None:
        """Write pull request analysis."""
        report.write(f"- **Total PRs Merged**: {pr_metrics['total_prs']}\n")
        report.write(f"- **Average PR Size**: {pr_metrics['avg_pr_size']:.0f} lines\n")
        report.write(f"- **Average PR Lifetime**: {pr_metrics['avg_pr_lifetime_hours']:.1f} hours\n")
        report.write(f"- **Story Point Coverage**: {pr_metrics['story_point_coverage']:.1f}%\n")
        
        if pr_metrics['total_review_comments'] > 0:
            report.write(f"- **Total Review Comments**: {pr_metrics['total_review_comments']}\n")
            avg_comments = pr_metrics['total_review_comments'] / pr_metrics['total_prs']
            report.write(f"- **Average Comments per PR**: {avg_comments:.1f}\n")
    
    def _write_ticket_tracking(self, report: StringIO, ticket_analysis: Dict[str, Any]) -> None:
        """Write ticket tracking analysis."""
        report.write("### Platform Usage\n\n")
        
        total_tickets = sum(ticket_analysis['ticket_summary'].values())
        
        for platform, count in sorted(ticket_analysis['ticket_summary'].items(), 
                                    key=lambda x: x[1], reverse=True):
            pct = count / total_tickets * 100 if total_tickets > 0 else 0
            report.write(f"- **{platform.title()}**: {count} tickets ({pct:.1f}%)\n")
        
        report.write(f"\n### Coverage Analysis\n\n")
        report.write(f"- **Commits with Tickets**: {ticket_analysis['commits_with_tickets']} ")
        report.write(f"of {ticket_analysis['total_commits']} ")
        report.write(f"({ticket_analysis['commit_coverage_pct']:.1f}%)\n")
        
        if ticket_analysis['untracked_commits']:
            report.write(f"\n### Significant Untracked Work\n\n")
            for commit in ticket_analysis['untracked_commits'][:5]:
                report.write(f"- `{commit['hash']}`: {commit['message']} ")
                report.write(f"({commit['files_changed']} files)\n")
    
    def _write_recommendations(self, report: StringIO, insights: List[Dict[str, Any]], 
                             ticket_analysis: Dict[str, Any], focus_data: List[Dict[str, Any]]) -> None:
        """Write recommendations based on analysis."""
        recommendations = []
        
        # Ticket coverage recommendations
        coverage = ticket_analysis['commit_coverage_pct']
        if coverage < 50:
            recommendations.append(
                "🎫 **Improve ticket tracking**: Current coverage is below 50%. "
                "Consider enforcing ticket references in commit messages or PR descriptions."
            )
        
        # Work distribution recommendations
        for insight in insights:
            if insight['insight'] == 'Work distribution':
                if 'unbalanced' in insight['value'].lower():
                    recommendations.append(
                        "⚖️ **Balance workload**: Work is concentrated among few developers. "
                        "Consider distributing tasks more evenly or adding team members."
                    )
        
        # Focus recommendations
        if focus_data:
            low_focus = [d for d in focus_data if d['focus_score'] < 50]
            if len(low_focus) > len(focus_data) / 2:
                recommendations.append(
                    "🎯 **Reduce context switching**: Many developers work across multiple projects. "
                    "Consider more focused project assignments to improve efficiency."
                )
        
        # Branching strategy
        for insight in insights:
            if insight['insight'] == 'Branching strategy' and 'Heavy' in insight['value']:
                recommendations.append(
                    "🌿 **Review branching strategy**: High percentage of merge commits suggests "
                    "complex branching. Consider simplifying the Git workflow."
                )
        
        if recommendations:
            for rec in recommendations:
                report.write(f"{rec}\n\n")
        else:
            report.write("✅ The team shows healthy development patterns. ")
            report.write("Continue current practices while monitoring for changes.\n")