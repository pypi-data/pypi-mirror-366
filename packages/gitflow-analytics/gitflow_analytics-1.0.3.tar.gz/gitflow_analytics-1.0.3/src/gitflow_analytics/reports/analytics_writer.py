"""Advanced analytics report generation with percentage and qualitative metrics."""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import pandas as pd
import numpy as np


class AnalyticsReportGenerator:
    """Generate advanced analytics reports with percentage breakdowns and qualitative insights."""
    
    def __init__(self, anonymize: bool = False):
        """Initialize analytics report generator."""
        self.anonymize = anonymize
        self._anonymization_map = {}
        self._anonymous_counter = 0
    
    def generate_activity_distribution_report(self, commits: List[Dict[str, Any]], 
                                            developer_stats: List[Dict[str, Any]],
                                            output_path: Path) -> Path:
        """Generate activity distribution report with percentage breakdowns."""
        # Build lookup maps
        dev_lookup = {dev['canonical_id']: dev for dev in developer_stats}
        
        # Calculate totals
        total_commits = len(commits)
        total_lines = sum(
            c.get('filtered_insertions', c.get('insertions', 0)) + 
            c.get('filtered_deletions', c.get('deletions', 0)) 
            for c in commits
        )
        total_files = sum(c['files_changed'] for c in commits)
        
        # Group by developer and project
        dev_project_activity = defaultdict(lambda: defaultdict(lambda: {
            'commits': 0, 'lines': 0, 'files': 0, 'story_points': 0
        }))
        
        for commit in commits:
            dev_id = commit.get('canonical_id', commit.get('author_email'))
            project = commit.get('project_key', 'UNKNOWN')
            
            dev_project_activity[dev_id][project]['commits'] += 1
            dev_project_activity[dev_id][project]['lines'] += (
                commit.get('filtered_insertions', commit.get('insertions', 0)) + 
                commit.get('filtered_deletions', commit.get('deletions', 0))
            )
            dev_project_activity[dev_id][project]['files'] += commit.get('filtered_files_changed', commit.get('files_changed', 0))
            dev_project_activity[dev_id][project]['story_points'] += commit.get('story_points', 0) or 0
        
        # Build report data
        rows = []
        
        for dev_id, projects in dev_project_activity.items():
            developer = dev_lookup.get(dev_id, {})
            dev_name = self._anonymize_value(developer.get('primary_name', 'Unknown'), 'name')
            
            # Calculate developer totals
            dev_total_commits = sum(p['commits'] for p in projects.values())
            dev_total_lines = sum(p['lines'] for p in projects.values())
            dev_total_files = sum(p['files'] for p in projects.values())
            
            for project, activity in projects.items():
                row = {
                    'developer': dev_name,
                    'project': project,
                    # Raw numbers
                    'commits': activity['commits'],
                    'lines_changed': activity['lines'],
                    'files_changed': activity['files'],
                    'story_points': activity['story_points'],
                    # Developer perspective (% of developer's time on this project)
                    'dev_commit_pct': round(activity['commits'] / dev_total_commits * 100, 1),
                    'dev_lines_pct': round(activity['lines'] / dev_total_lines * 100, 1) if dev_total_lines > 0 else 0,
                    'dev_files_pct': round(activity['files'] / dev_total_files * 100, 1) if dev_total_files > 0 else 0,
                    # Project perspective (% of project work by this developer)
                    'proj_commit_pct': round(activity['commits'] / total_commits * 100, 1),
                    'proj_lines_pct': round(activity['lines'] / total_lines * 100, 1) if total_lines > 0 else 0,
                    'proj_files_pct': round(activity['files'] / total_files * 100, 1) if total_files > 0 else 0,
                    # Overall perspective (% of total activity)
                    'total_activity_pct': round(activity['commits'] / total_commits * 100, 1)
                }
                rows.append(row)
        
        # Sort by total activity
        rows.sort(key=lambda x: x['total_activity_pct'], reverse=True)
        
        # Write CSV
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def generate_qualitative_insights_report(self, commits: List[Dict[str, Any]],
                                           developer_stats: List[Dict[str, Any]],
                                           ticket_analysis: Dict[str, Any],
                                           output_path: Path) -> Path:
        """Generate qualitative insights and patterns report."""
        insights = []
        
        # Analyze commit patterns
        commit_insights = self._analyze_commit_patterns(commits)
        insights.extend(commit_insights)
        
        # Analyze developer patterns
        dev_insights = self._analyze_developer_patterns(commits, developer_stats)
        insights.extend(dev_insights)
        
        # Analyze collaboration patterns
        collab_insights = self._analyze_collaboration_patterns(commits)
        insights.extend(collab_insights)
        
        # Analyze work distribution
        dist_insights = self._analyze_work_distribution(commits)
        insights.extend(dist_insights)
        
        # Write insights to CSV
        df = pd.DataFrame(insights)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def generate_developer_focus_report(self, commits: List[Dict[str, Any]],
                                      developer_stats: List[Dict[str, Any]],
                                      output_path: Path,
                                      weeks: int = 12) -> Path:
        """Generate developer focus analysis showing concentration patterns and activity across all projects."""
        # Calculate week boundaries (timezone-aware to match commit timestamps)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(weeks=weeks)
        
        # Build developer lookup
        dev_lookup = {dev['canonical_id']: dev for dev in developer_stats}
        
        # Get all unique projects
        all_projects = sorted(list(set(c.get('project_key', 'UNKNOWN') for c in commits)))
        
        # Analyze focus patterns
        focus_data = []
        
        # Calculate total commits per project for percentage calculations
        project_totals = defaultdict(int)
        for commit in commits:
            project_totals[commit.get('project_key', 'UNKNOWN')] += 1
        
        total_commits = len(commits)
        
        for dev in developer_stats:
            dev_id = dev['canonical_id']
            dev_name = self._anonymize_value(dev['primary_name'], 'name')
            
            # Get developer's commits
            dev_commits = [c for c in commits if c.get('canonical_id') == dev_id]
            if not dev_commits:
                continue
            
            # Calculate focus metrics
            projects = defaultdict(int)
            project_lines = defaultdict(int)
            weekly_activity = defaultdict(int)
            commit_sizes = []
            commit_hours = []
            
            for commit in dev_commits:
                # Project distribution
                project_key = commit.get('project_key', 'UNKNOWN')
                projects[project_key] += 1
                
                # Lines changed per project
                lines_changed = (
                    commit.get('filtered_insertions', commit.get('insertions', 0)) + 
                    commit.get('filtered_deletions', commit.get('deletions', 0))
                )
                project_lines[project_key] += lines_changed
                
                # Weekly distribution
                week_start = self._get_week_start(commit['timestamp'])
                weekly_activity[week_start] += 1
                
                # Commit size
                commit_sizes.append(lines_changed)
                
                # Time of day
                if hasattr(commit['timestamp'], 'hour'):
                    commit_hours.append(commit['timestamp'].hour)
            
            # Calculate metrics
            num_projects = len(projects)
            primary_project = max(projects, key=projects.get) if projects else 'UNKNOWN'
            primary_project_pct = round(projects[primary_project] / len(dev_commits) * 100, 1)
            
            # Focus score (100% = single project, lower = more scattered)
            focus_score = round(100 / num_projects if num_projects > 0 else 0, 1)
            
            # Consistency score (active weeks / total weeks)
            active_weeks = len(weekly_activity)
            consistency_score = round(active_weeks / weeks * 100, 1)
            
            # Work pattern
            avg_commit_size = np.mean(commit_sizes) if commit_sizes else 0
            if avg_commit_size < 50:
                work_style = "Small, frequent changes"
            elif avg_commit_size < 200:
                work_style = "Moderate batch changes"
            else:
                work_style = "Large batch changes"
            
            # Time pattern
            if commit_hours:
                avg_hour = np.mean(commit_hours)
                if avg_hour < 10:
                    time_pattern = "Morning developer"
                elif avg_hour < 14:
                    time_pattern = "Midday developer"
                elif avg_hour < 18:
                    time_pattern = "Afternoon developer"
                else:
                    time_pattern = "Evening developer"
            else:
                time_pattern = "Unknown"
            
            # Build the row with basic metrics
            row = {
                'developer': dev_name,
                'total_commits': len(dev_commits),
                'num_projects': num_projects,
                'primary_project': primary_project,
                'primary_project_pct': primary_project_pct,
                'focus_score': focus_score,
                'active_weeks': active_weeks,
                'consistency_score': consistency_score,
                'avg_commit_size': round(avg_commit_size, 1),
                'work_style': work_style,
                'time_pattern': time_pattern
            }
            
            # Add project-specific metrics
            for project in all_projects:
                # Gross commits
                gross_commits = projects.get(project, 0)
                row[f'{project}_gross_commits'] = gross_commits
                
                # Adjusted commits (weighted by lines changed)
                if gross_commits > 0 and project_lines[project] > 0:
                    # Adjustment factor based on average lines per commit
                    project_avg_lines = project_lines[project] / gross_commits
                    overall_avg_lines = sum(commit_sizes) / len(commit_sizes) if commit_sizes else 1
                    adjustment_factor = project_avg_lines / overall_avg_lines if overall_avg_lines > 0 else 1
                    adjusted_commits = round(gross_commits * adjustment_factor, 1)
                else:
                    adjusted_commits = 0
                row[f'{project}_adjusted_commits'] = adjusted_commits
                
                # Percent of developer's activity
                dev_pct = round(gross_commits / len(dev_commits) * 100, 1) if len(dev_commits) > 0 else 0
                row[f'{project}_dev_pct'] = dev_pct
                
                # Percent of project's total activity
                proj_pct = round(gross_commits / project_totals[project] * 100, 1) if project_totals[project] > 0 else 0
                row[f'{project}_proj_pct'] = proj_pct
                
                # Percent of total repository activity
                total_pct = round(gross_commits / total_commits * 100, 1) if total_commits > 0 else 0
                row[f'{project}_total_pct'] = total_pct
            
            focus_data.append(row)
        
        # Sort by focus score
        focus_data.sort(key=lambda x: x['focus_score'], reverse=True)
        
        # Write CSV
        df = pd.DataFrame(focus_data)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def _analyze_commit_patterns(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze patterns in commit data."""
        insights = []
        
        # Time-based patterns
        commit_hours = [c['timestamp'].hour for c in commits if hasattr(c['timestamp'], 'hour')]
        if commit_hours:
            peak_hour = max(set(commit_hours), key=commit_hours.count)
            insights.append({
                'category': 'Timing',
                'insight': 'Peak commit hour',
                'value': f"{peak_hour}:00",
                'impact': 'Indicates team working hours'
            })
        
        # Commit message patterns
        message_lengths = [len(c['message'].split()) for c in commits]
        avg_message_length = np.mean(message_lengths)
        
        if avg_message_length < 5:
            quality = "Very brief"
        elif avg_message_length < 10:
            quality = "Concise"
        elif avg_message_length < 20:
            quality = "Detailed"
        else:
            quality = "Very detailed"
        
        insights.append({
            'category': 'Quality',
            'insight': 'Commit message quality',
            'value': quality,
            'impact': f"Average {avg_message_length:.1f} words per message"
        })
        
        # Ticket coverage insights
        commits_with_tickets = sum(1 for c in commits if c.get('ticket_references'))
        coverage_pct = commits_with_tickets / len(commits) * 100 if commits else 0
        
        if coverage_pct < 30:
            tracking = "Poor tracking"
        elif coverage_pct < 60:
            tracking = "Moderate tracking"
        elif coverage_pct < 80:
            tracking = "Good tracking"
        else:
            tracking = "Excellent tracking"
        
        insights.append({
            'category': 'Process',
            'insight': 'Ticket tracking adherence',
            'value': tracking,
            'impact': f"{coverage_pct:.1f}% commits have ticket references"
        })
        
        return insights
    
    def _analyze_developer_patterns(self, commits: List[Dict[str, Any]], 
                                  developer_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze developer behavior patterns."""
        insights = []
        
        # Team size insights
        team_size = len(developer_stats)
        if team_size < 3:
            team_type = "Very small team"
        elif team_size < 6:
            team_type = "Small team"
        elif team_size < 12:
            team_type = "Medium team"
        else:
            team_type = "Large team"
        
        insights.append({
            'category': 'Team',
            'insight': 'Team size',
            'value': team_type,
            'impact': f"{team_size} active developers"
        })
        
        # Contribution distribution
        commit_counts = [dev['total_commits'] for dev in developer_stats]
        if commit_counts:
            gini_coef = self._calculate_gini_coefficient(commit_counts)
            
            if gini_coef < 0.3:
                distribution = "Very balanced"
            elif gini_coef < 0.5:
                distribution = "Moderately balanced"
            elif gini_coef < 0.7:
                distribution = "Somewhat unbalanced"
            else:
                distribution = "Highly concentrated"
            
            insights.append({
                'category': 'Team',
                'insight': 'Work distribution',
                'value': distribution,
                'impact': f"Gini coefficient: {gini_coef:.2f}"
            })
        
        return insights
    
    def _analyze_collaboration_patterns(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze collaboration patterns."""
        insights = []
        
        # Merge commit analysis
        merge_commits = [c for c in commits if c.get('is_merge')]
        merge_pct = len(merge_commits) / len(commits) * 100 if commits else 0
        
        if merge_pct < 5:
            branching = "Minimal branching"
        elif merge_pct < 15:
            branching = "Moderate branching"
        elif merge_pct < 25:
            branching = "Active branching"
        else:
            branching = "Heavy branching"
        
        insights.append({
            'category': 'Workflow',
            'insight': 'Branching strategy',
            'value': branching,
            'impact': f"{merge_pct:.1f}% merge commits"
        })
        
        return insights
    
    def _analyze_work_distribution(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze work distribution patterns."""
        insights = []
        
        # File change patterns
        file_changes = [c['files_changed'] for c in commits if c['files_changed'] > 0]
        if file_changes:
            avg_files = np.mean(file_changes)
            
            if avg_files < 3:
                pattern = "Focused changes"
            elif avg_files < 8:
                pattern = "Moderate scope changes"
            else:
                pattern = "Broad scope changes"
            
            insights.append({
                'category': 'Workflow',
                'insight': 'Change scope pattern',
                'value': pattern,
                'impact': f"Average {avg_files:.1f} files per commit"
            })
        
        return insights
    
    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for distribution analysis."""
        if not values or len(values) == 1:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(values)
        cumsum = np.cumsum(sorted_values)
        return (2 * np.sum((i + 1) * sorted_values[i] for i in range(n))) / (n * cumsum[-1]) - (n + 1) / n
    
    def _get_week_start(self, date: datetime) -> datetime:
        """Get Monday of the week for a given date."""
        # Ensure consistent timezone handling - keep timezone info
        if hasattr(date, 'tzinfo') and date.tzinfo is not None:
            # Keep timezone-aware but ensure it's UTC
            if date.tzinfo != timezone.utc:
                date = date.astimezone(timezone.utc)
        else:
            # Convert naive datetime to UTC timezone-aware
            date = date.replace(tzinfo=timezone.utc)
        
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)
        return monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _anonymize_value(self, value: str, field_type: str) -> str:
        """Anonymize a value if anonymization is enabled."""
        if not self.anonymize or not value:
            return value
        
        if value not in self._anonymization_map:
            self._anonymous_counter += 1
            if field_type == 'name':
                anonymous = f"Developer{self._anonymous_counter}"
            else:
                anonymous = f"anon{self._anonymous_counter}"
            self._anonymization_map[value] = anonymous
        
        return self._anonymization_map[value]