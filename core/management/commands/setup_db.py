import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Run all SQL setup scripts (schema, triggers, procedures, mock data)'

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        host = db.get('HOST', 'localhost')
        port = db.get('PORT', '3306')
        user = db['USER']
        password = db.get('PASSWORD', '')
        name = db['NAME']

        # Order matters!
        sql_files = [
            'sql/01_schema.sql',
            'sql/02_phase2_triggers.sql',
            'sql/03_phase2_procedures.sql',
            'sql/04_geographic_procedures.sql',
            'sql/05_phase3_auth.sql',
            'sql/06_phase4_procedures.sql',
            'sql/07_phase5_procedures_triggers.sql',
            'sql/mock_data.sql',
        ]

        for sql_file in sql_files:
            self.stdout.write(f'Running {sql_file} ...')
            cmd = f'mysql -h {host} -P {port} -u {user} -p{password} {name} < {sql_file}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                self.stderr.write(f'Error in {sql_file}:\n{result.stderr}')
                return
            else:
                self.stdout.write(self.style.SUCCESS(f'{sql_file} executed successfully.'))

        self.stdout.write(self.style.SUCCESS('Database setup complete!'))