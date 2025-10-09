# filters.py
import django_filters
from django.utils import timezone
from datetime import timedelta
from app.models import Job
from app.utils import getJobsOpeningsByCategories,getZones
import pdb
class JobFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=[])
    zone = django_filters.ChoiceFilter(field_name='zone__id', choices=[])
    
    job_type = django_filters.MultipleChoiceFilter(
        choices=[
            ('Full Time', 'Full Time'),
            ('Part Time', 'Part Time'),
            ('Remote', 'Remote'),
            ('Freelance', 'Freelance'),
        ]
    )
    
    experience = django_filters.MultipleChoiceFilter(
        choices=[
            ('1-2 Years', '1-2 Years'),
            ('2-3 Years', '2-3 Years'),
            ('3-6 Years', '3-6 Years'),
            ('6+ Years', '6+ Years'),
        ],
        method='filter_experience'
    )
    
    posted_within = django_filters.MultipleChoiceFilter(
        choices=[
            ('Today', 'Today'),
            ('Last 2 days', 'Last 2 days'),
            ('Last 3 days', 'Last 3 days'),
            ('Last 5 days', 'Last 5 days'),
            ('Last 10 days', 'Last 10 days'),
        ],
        method='filter_posted_within'
    )
    
    salary_range = django_filters.RangeFilter(
        method='filter_salary',
        label='Salary Range'
    )

    class Meta:
        model = Job
        fields = []

    def __init__(self, *args, **kwargs):
        # Get categories and zones from kwargs or use empty lists
        self.categories = kwargs.pop('categories', [])
        self.zones = kwargs.pop('zones', [])
        super().__init__(*args, **kwargs)
        
        # Set choices dynamically
        self.filters['category'].extra['choices'] = self.get_category_choices()
        self.filters['zone'].extra['choices'] = self.get_zone_choices()

    def get_category_choices(self):
        choices = [('', 'Select Category')]
        for cat in self.categories:
            # Handle both dictionary and object types
            if isinstance(cat, dict):
                key = cat.get('key', '')
                name = cat.get('name', '')
            else:
                key = getattr(cat, 'key', '')
                name = getattr(cat, 'name', '')
            if key and name:
                choices.append((key, name))
        return choices

    def get_zone_choices(self):
        choices = [('', 'Select Location')]
        for zone in self.zones:
            # Handle both dictionary and object types
            if isinstance(zone, dict):
                zone_id = zone.get('id', '')
                name = zone.get('name', '')
            else:
                zone_id = getattr(zone, 'id', '')
                name = getattr(zone, 'name', '')
            if zone_id and name:
                choices.append((zone_id, name))
        return choices

    def filter_experience(self, queryset, name, value):
        experience_map = {
            '1-2 Years': 1, 
            '2-3 Years': 2,
            '3-6 Years': 3, 
            '6+ Years': 6
        }
        experience_values = [experience_map[exp] for exp in value if exp in experience_map]
        if experience_values:
            return queryset.filter(experience_needed__in=experience_values)
        return queryset

    def filter_posted_within(self, queryset, name, value):
        today = timezone.now().date()
        date_filters = []
        
        for option in value:
            if option == 'Today':
                date_filters.append(today)
            elif option == 'Last 2 days':
                date_filters.extend([today - timedelta(days=i) for i in range(2)])
            elif option == 'Last 3 days':
                date_filters.extend([today - timedelta(days=i) for i in range(3)])
            elif option == 'Last 5 days':
                date_filters.extend([today - timedelta(days=i) for i in range(5)])
            elif option == 'Last 10 days':
                date_filters.extend([today - timedelta(days=i) for i in range(10)])
        
        if date_filters:
            unique_dates = list(set(date_filters))
            return queryset.filter(timestamp__date__in=unique_dates)
        return queryset

    def filter_salary(self, queryset, name, value):
        if value.start is not None and value.stop is not None:
            return queryset.filter(
                min_salary__gte=value.start,
                max_salary__lte=value.stop
            )
        return queryset