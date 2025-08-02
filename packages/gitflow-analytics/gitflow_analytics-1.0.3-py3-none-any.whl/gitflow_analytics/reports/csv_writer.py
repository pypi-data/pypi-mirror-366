"""CSV report generation for GitFlow Analytics."""
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import pandas as pd


class CSVReportGenerator:
    """Generate CSV reports with weekly metrics."""
    
    def __init__(self, anonymize: bool = False):
        """Initialize report generator."""
        self.anonymize = anonymize
        self._anonymization_map: Dict[str, str] = {}
        self._anonymous_counter = 0
    
    def generate_weekly_report(self, commits: List[Dict[str, Any]], 
                             developer_stats: List[Dict[str, Any]],
                             output_path: Path,
                             weeks: int = 12) -> Path:
        """Generate weekly metrics CSV report."""
        # Calculate week boundaries (timezone-aware to match commit timestamps)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(weeks=weeks)
        
        # Group commits by week and developer
        weekly_data: Dict[Tuple[datetime, str, str], Dict[str, Any]] = self._aggregate_weekly_data(commits, start_date, end_date)
        
        # Create developer lookup
        dev_lookup = {dev['canonical_id']: dev for dev in developer_stats}
        
        # Build CSV rows
        rows = []
        for (week_start, canonical_id, project_key), metrics in weekly_data.items():
            developer = dev_lookup.get(canonical_id, {})
            
            row = {
                'week_start': week_start.strftime('%Y-%m-%d'),
                'developer_id': self._anonymize_value(canonical_id, 'id'),
                'developer_name': self._anonymize_value(
                    developer.get('primary_name', 'Unknown'), 'name'
                ),
                'developer_email': self._anonymize_value(
                    developer.get('primary_email', 'unknown@example.com'), 'email'
                ),
                'project': project_key,
                'commits': metrics['commits'],
                'story_points': metrics['story_points'],
                'lines_added': metrics['lines_added'],
                'lines_removed': metrics['lines_removed'],
                'files_changed': metrics['files_changed'],
                'complexity_delta': round(metrics['complexity_delta'], 2),
                'ticket_coverage_pct': round(metrics['ticket_coverage_pct'], 1),
                'avg_commit_size': round(metrics['avg_commit_size'], 1),
                'unique_tickets': metrics['unique_tickets'],
                'prs_involved': metrics['prs_involved']
            }
            rows.append(row)
        
        # Sort by week and developer
        rows.sort(key=lambda x: (x['week_start'], x['developer_name'], x['project']))
        
        # Write CSV
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False)
        else:
            # Write empty CSV with headers
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'week_start', 'developer_id', 'developer_name', 'developer_email',
                    'project', 'commits', 'story_points', 'lines_added', 'lines_removed',
                    'files_changed', 'complexity_delta', 'ticket_coverage_pct',
                    'avg_commit_size', 'unique_tickets', 'prs_involved'
                ])
                writer.writeheader()
        
        return output_path
    
    def generate_summary_report(self, commits: List[Dict[str, Any]],
                              prs: List[Dict[str, Any]],
                              developer_stats: List[Dict[str, Any]],
                              ticket_analysis: Dict[str, Any],
                              output_path: Path) -> Path:
        """Generate summary statistics CSV."""
        summary_data = []
        
        # Overall statistics
        total_commits = len(commits)
        total_story_points = sum(c.get('story_points', 0) or 0 for c in commits)
        # Use filtered stats if available, otherwise fall back to raw stats
        total_lines = sum(
            c.get('filtered_insertions', c.get('insertions', 0)) + 
            c.get('filtered_deletions', c.get('deletions', 0)) 
            for c in commits
        )
        
        summary_data.append({
            'metric': 'Total Commits',
            'value': total_commits,
            'category': 'Overall'
        })
        
        summary_data.append({
            'metric': 'Total Story Points',
            'value': total_story_points,
            'category': 'Overall'
        })
        
        summary_data.append({
            'metric': 'Total Lines Changed',
            'value': total_lines,
            'category': 'Overall'
        })
        
        summary_data.append({
            'metric': 'Active Developers',
            'value': len(developer_stats),
            'category': 'Overall'
        })
        
        # Ticket coverage
        summary_data.append({
            'metric': 'Commit Ticket Coverage %',
            'value': round(ticket_analysis.get('commit_coverage_pct', 0), 1),
            'category': 'Tracking'
        })
        
        summary_data.append({
            'metric': 'PR Ticket Coverage %',
            'value': round(ticket_analysis.get('pr_coverage_pct', 0), 1),
            'category': 'Tracking'
        })
        
        # Platform breakdown
        for platform, count in ticket_analysis.get('ticket_summary', {}).items():
            summary_data.append({
                'metric': f'{platform.title()} Tickets',
                'value': count,
                'category': 'Platforms'
            })
        
        # Developer statistics
        if developer_stats:
            top_contributor = max(developer_stats, key=lambda x: x['total_commits'])
            summary_data.append({
                'metric': 'Top Contributor',
                'value': self._anonymize_value(top_contributor['primary_name'], 'name'),
                'category': 'Developers'
            })
            
            summary_data.append({
                'metric': 'Top Contributor Commits',
                'value': top_contributor['total_commits'],
                'category': 'Developers'
            })
        
        # Write summary CSV
        df = pd.DataFrame(summary_data)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def generate_developer_report(self, developer_stats: List[Dict[str, Any]],
                                output_path: Path) -> Path:
        """Generate developer statistics CSV."""
        rows = []
        
        for dev in developer_stats:
            row = {
                'developer_id': self._anonymize_value(dev['canonical_id'], 'id'),
                'name': self._anonymize_value(dev['primary_name'], 'name'),
                'email': self._anonymize_value(dev['primary_email'], 'email'),
                'github_username': self._anonymize_value(
                    dev.get('github_username', ''), 'username'
                ) if dev.get('github_username') else '',
                'total_commits': dev['total_commits'],
                'total_story_points': dev['total_story_points'],
                'alias_count': dev['alias_count'],
                'first_seen': dev['first_seen'].strftime('%Y-%m-%d') if dev['first_seen'] else '',
                'last_seen': dev['last_seen'].strftime('%Y-%m-%d') if dev['last_seen'] else '',
                'avg_story_points_per_commit': round(
                    dev['total_story_points'] / max(dev['total_commits'], 1), 2
                )
            }
            rows.append(row)
        
        # Sort by total commits
        rows.sort(key=lambda x: x['total_commits'], reverse=True)
        
        # Write CSV
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def _aggregate_weekly_data(self, commits: List[Dict[str, Any]], 
                             start_date: datetime, 
                             end_date: datetime) -> Dict[Tuple[datetime, str, str], Dict[str, Any]]:
        """Aggregate commit data by week."""
        weekly_data: defaultdict[Tuple[datetime, str, str], Dict[str, Any]] = defaultdict(lambda: {
            'commits': 0,
            'story_points': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'files_changed': 0,
            'complexity_delta': 0.0,
            'commits_with_tickets': 0,
            'tickets': set(),
            'prs': set()
        })
        
        for commit in commits:
            timestamp = commit['timestamp']
            # Ensure consistent timezone handling
            if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
                # Keep timezone-aware but ensure it's UTC
                if timestamp.tzinfo != timezone.utc:
                    timestamp = timestamp.astimezone(timezone.utc)
            else:
                # Convert naive datetime to UTC timezone-aware
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            
            if timestamp < start_date or timestamp > end_date:
                continue
            
            # Get week start (Monday)
            week_start = self._get_week_start(timestamp)
            
            # Get project key (default to 'unknown')
            project_key = commit.get('project_key', 'unknown')
            
            # Get canonical developer ID
            canonical_id = commit.get('canonical_id', commit.get('author_email', 'unknown'))
            
            key = (week_start, canonical_id, project_key)
            
            # Aggregate metrics
            data = weekly_data[key]
            data['commits'] += 1
            data['story_points'] += commit.get('story_points', 0) or 0
            
            # Use filtered stats if available, otherwise fall back to raw stats
            data['lines_added'] += commit.get('filtered_insertions', commit.get('insertions', 0)) or 0
            data['lines_removed'] += commit.get('filtered_deletions', commit.get('deletions', 0)) or 0
            data['files_changed'] += commit.get('filtered_files_changed', commit.get('files_changed', 0)) or 0
            
            data['complexity_delta'] += commit.get('complexity_delta', 0.0) or 0.0
            
            # Track tickets
            ticket_refs = commit.get('ticket_references', [])
            if ticket_refs:
                data['commits_with_tickets'] += 1
                tickets_set = data['tickets']
                for ticket in ticket_refs:
                    if isinstance(ticket, dict):
                        tickets_set.add(ticket.get('full_id', ''))
                    else:
                        tickets_set.add(str(ticket))
            
            # Track PRs (if available)
            pr_number = commit.get('pr_number')
            if pr_number:
                prs_set = data['prs']
                prs_set.add(pr_number)
        
        # Calculate derived metrics
        result: Dict[Tuple[datetime, str, str], Dict[str, Any]] = {}
        for key, metrics in weekly_data.items():
            commits_count = metrics['commits']
            if commits_count > 0:
                metrics['ticket_coverage_pct'] = (
                    metrics['commits_with_tickets'] / commits_count * 100
                )
                metrics['avg_commit_size'] = (
                    (metrics['lines_added'] + metrics['lines_removed']) / commits_count
                )
            else:
                metrics['ticket_coverage_pct'] = 0
                metrics['avg_commit_size'] = 0
            
            tickets_set = metrics['tickets']
            prs_set = metrics['prs']
            metrics['unique_tickets'] = len(tickets_set)
            metrics['prs_involved'] = len(prs_set)
            
            # Remove sets before returning
            del metrics['tickets']
            del metrics['prs']
            del metrics['commits_with_tickets']
            
            result[key] = metrics
        
        return result
    
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
        
        if field_type == 'email' and '@' in value:
            # Keep domain for email
            local, domain = value.split('@', 1)
            value = local  # Anonymize only local part
            suffix = f"@{domain}"
        else:
            suffix = ""
        
        if value not in self._anonymization_map:
            self._anonymous_counter += 1
            if field_type == 'name':
                anonymous = f"Developer{self._anonymous_counter}"
            elif field_type == 'email':
                anonymous = f"dev{self._anonymous_counter}"
            elif field_type == 'id':
                anonymous = f"ID{self._anonymous_counter:04d}"
            else:
                anonymous = f"anon{self._anonymous_counter}"
            
            self._anonymization_map[value] = anonymous
        
        return self._anonymization_map[value] + suffix