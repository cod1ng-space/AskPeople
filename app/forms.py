from hmac import new
from django import forms
from django.contrib.auth.models import User

from app.models import Answer, Profile, Question

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and username[0].lower() == 'b':
            raise forms.ValidationError('You failed!')
        if username and not username.isalnum():
            raise forms.ValidationError('Username must contain only letters and digits.')
        return username

class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your login here'}),
        help_text='No more than 30 characters in total'
    )

    email = forms.EmailField(max_length=100, required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email here'})
    )
    
    password = forms.CharField(max_length=150, required=True, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password here'}),
        help_text='Minimum 8 characters'
    )
    
    password_repeat = forms.CharField(max_length=150, required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat your password here'}),
        help_text='Minimum 8 characters'
    )
    
    avatar = forms.ImageField(required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text='JPEG or PNG, max 2MB'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_repeat', 'avatar']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_repeat = cleaned_data.get('password_repeat')

        if password and len(password) < 8:
            self.add_error('password', 'Password must be at least 8 characters long.')

        if password and password_repeat and password != password_repeat:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                avatar=self.cleaned_data.get('avatar')
            )
        return user

class UserEditForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Leave blank to keep current'}),
        help_text='No more than 30 characters in total'
    )

    email = forms.EmailField(max_length=100, required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Leave blank to keep current'})
    )

    new_password = forms.CharField(max_length=150, required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current'}),
        help_text='Minimum 8 characters (leave blank to keep current)'
    )
    
    password_repeat = forms.CharField(max_length=150,required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat new password if changing'})
    )
    
    avatar = forms.ImageField(required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text='JPEG or PNG, max 2MB'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'new_password', 'password_repeat', 'avatar']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_username = self.instance.username
        self.initial_email = self.instance.email
        if hasattr(self.instance, 'profile'):
            self.initial_avatar = self.instance.profile.avatar
            
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        password_repeat = cleaned_data.get('password_repeat')

        if new_password:
            if len(new_password) < 8:
                self.add_error('new_password', 'Password must be at least 8 characters long.')
            if new_password != password_repeat:
                self.add_error('password_repeat', "Passwords don't match")
        
        fields_changed = False
        
        username = cleaned_data.get('username')
        if username and username != self.initial_username:
            fields_changed = True

        email = cleaned_data.get('email')
        if email and email != self.initial_email:
            fields_changed = True

        if new_password:
            fields_changed = True

        avatar = cleaned_data.get('avatar')
        if avatar is not None:
            fields_changed = True

        if not fields_changed:
            raise forms.ValidationError('No changes detected. Please update at least one field.')
        
        return cleaned_data

    def save(self, commit=True):
        user = self.instance
        profile = getattr(user, 'profile', None)

        username = self.cleaned_data.get('username')
        if username and username != self.initial_username:
            user.username = username

        email = self.cleaned_data.get('email')
        if email and email != self.initial_email:
            user.email = email

        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()

            avatar = self.cleaned_data.get('avatar')
            if avatar is not None:
                if profile is None:
                    profile = Profile(user=user)
                profile.avatar = avatar
                profile.save()

        return user

class AskForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter the tags separated by commas'}),
        help_text='1 to 3 comma-separated tags'
    )

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter the question title'}),
            'text': forms.Textarea(attrs={'placeholder': 'Enter the question text', 'rows': 5}),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]
        if not (1 <= len(tag_names) <= 3):
            raise forms.ValidationError('Enter 1 to 3 comma-separated tags')
        return tag_names

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Write your answer here',
                'rows': 3,
                'class': 'answer-textarea',
            }),
        }
        labels = {'text': '', }