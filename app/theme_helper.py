# theme_helper.py

from typing import Any, Optional, Dict

# Central site configuration dictionary
site_configs: Dict[str, Any] = {
    'site_name': 'Omeiat',
    'site_description': 'ORGANISATION OF MUSLIM EDUCATIONAL INSTITUTES AND ASSOCIATIONS OF TAMILNADU',
    'site_keywords': 'Job Portal, Career Opportunities, Recruitment, Job Search, Apply Now, Upload Resume, Vacancies, Job Openings, Hiring, We Are Hiring, Job Seeker, Candidate Profile, Resume Builder, Skills & Experience, Work History, Education Details, Shortlisted, Applied Jobs, Interview Scheduled, Job Alerts, Employer Dashboard, Post a Job, Manage Applications, Candidate Shortlist, Company Profile, Organization Overview, Recruiter Panel, Hiring Status, Interview Feedback, Application Status, Filters, Job Categories, Remote Jobs, Full-time, Part-time, Internship, Saved Jobs, Job Recommendations',
    'site_author': 'Abutalib Noormohammed | Beternal Techno Solutions',
    'site_url': 'https://www.omeiat-emp.com',
    'site_logo': '/static/images/logo/logo.png',
    'site_favicon': '/static/images/favicon/favicon.ico',
    'site_social_links': {
        'facebook': 'https://www.facebook.com/YourPage',
    },
    'site_contact_email': 'info@omeiat.in',
    'site_contact_phone': '044-48566559',
    'site_address': '#147, The New College campus, Peters Road, Royapettah,',
    'site_copyright': '© 2025 Omeiat. All rights reserved.',
    'site_privacy_policy_url': '/privacy-policy/',
    'site_terms_of_service_url': '/terms-of-service/',
    'site_cookie_policy_url': '/cookie-policy/',
    'site_language': 'en',
    'site_locale': 'en_US',
    'site_timezone': 'UTC',
    'site_analytics_id': '',
    'site_analytics_provider': 'Google Analytics',
    'site_analytics_script': '',
    'site_custom_css': '',
    'site_custom_js': '',
    'site_enable_comments': True,
    'site_comments_provider': 'Disqus',
    'site_enable_search': True,
    'site_search_provider': 'Google Custom Search',
    'site_enable_social_sharing': True,
    'site_social_sharing_provider': 'AddThis'
}

def get_site_config(key: str, default: Optional[Any] = None) -> Any:
    """
    Get a specific configuration value by key.
    """
    return site_configs.get(key, default)

def get_site_config():
    return site_configs

def set_site_config(key: str, value: Any) -> None:
    """
    Set a specific configuration value by key.
    """
    site_configs[key] = value

def get_site_configs() -> Dict[str, Any]:
    """
    Return the entire site configuration dictionary.
    """
    return site_configs

def update_site_config(new_configs: Dict[str, Any]) -> None:
    """
    Update multiple configuration values at once.
    """
    if not isinstance(new_configs, dict):
        raise ValueError("update_site_config() expects a dictionary")
    
    site_configs.update(new_configs)
