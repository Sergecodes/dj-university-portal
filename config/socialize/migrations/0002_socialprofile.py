# Generated by Django 3.1.3 on 2021-08-20 09:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('marketplace', '0002_auto_20210820_0941'),
        ('socialize', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialProfile',
            fields=[
                ('about_me', models.TextField(verbose_name='A little about me')),
                ('about_me_en', models.TextField(null=True, verbose_name='A little about me')),
                ('about_me_fr', models.TextField(null=True, verbose_name='A little about me')),
                ('hobbies', models.TextField(verbose_name='My hobbies and interests')),
                ('hobbies_en', models.TextField(null=True, verbose_name='My hobbies and interests')),
                ('hobbies_fr', models.TextField(null=True, verbose_name='My hobbies and interests')),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('is_visible', models.BooleanField(default=False, help_text='<br>Enable Socialize and allow other users to be able to view my profile.', verbose_name='Profile visible to other users')),
                ('birth_date', models.DateField(help_text='Please at least enter the correct birth year.', verbose_name='Birthday')),
                ('department', models.CharField(max_length=30, verbose_name='Department')),
                ('department_en', models.CharField(max_length=30, null=True, verbose_name='Department')),
                ('department_fr', models.CharField(max_length=30, null=True, verbose_name='Department')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='social_profile', serialize=False, to='users.user')),
                ('level', models.CharField(choices=[('L1', 'Level 1'), ('L2', 'Level 2'), ('L3', 'Level 3'), ('L4', 'Level 5'), ('M', 'Masters'), ('PhD', 'Doctorate'), ('Other', 'Other')], default=None, max_length=7, verbose_name='Level')),
                ('current_relationship', models.CharField(choices=[('single', 'Single'), ('dating', 'Dating'), ('engaged', 'Engaged'), ('married', 'Married'), ('undecided', 'Undecided')], default=None, max_length=15, verbose_name='Current relationship')),
                ('interested_relationship', models.CharField(choices=[('chatting', 'Being chat pals'), ('studies', 'Being study pals'), ('clubbing', 'Clubbing this weekend'), ('dating', 'Dating'), ('flirting', 'Flirting'), ('friendship', 'Friendship'), ('hanging_out', 'Hanging out this weekend'), ('marriage', 'Marriage'), ('undecided', 'Undecided')], default=None, max_length=15, verbose_name='Interested relationship')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], default='M', max_length=2, verbose_name='Gender')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='social_profiles', related_query_name='social_profile', to='marketplace.institution')),
                ('social_media', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='socialize.socialmediafollow')),
            ],
        ),
    ]