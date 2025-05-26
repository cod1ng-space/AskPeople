from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from django.db.models.functions import Coalesce

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class TagManager(models.Manager):
    def popular(self, limit=10):
        return self.annotate(
            num_questions=Count('question')
        ).order_by('-num_questions')[:limit]
    
class Tag(models.Model):
    COLOR_CHOICES = [
        ("pri", "primary"),
        ("sec", "secondary"),
        ("suc", "success"),
        ("dan", "danger"),
        ("war", "warning"),
        ("inf", "info"),
        ("lig", "light"),
        ("dar", "dark"),
    ]

    name = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=3, choices=COLOR_CHOICES, default="pri")

    objects = TagManager()

    @property
    def get_color(self):
        return dict(self.COLOR_CHOICES).get(self.color, "primary")

    def __str__(self):
        return self.name
    
class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-created_at')

    def hot(self):
        return self.with_ratings().order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self.filter(tags__name=tag_name).order_by('-created_at')
    
    def with_ratings(self):
        return self.annotate(
            like_count=Count('questionlike', filter=Q(questionlike__value=1)),
            dislike_count=Count('questionlike', filter=Q(questionlike__value=-1)),
            rating=Coalesce(Sum('questionlike__value'), 0)
        )

class Question(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=2000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_url(self):
        return f'/question/{self.id}'

    def answers_count(self):
        return self.answer_set.count()

    def likes_count(self):
        return self.questionlike_set.filter(value=1).count()
    
    def dislikes_count(self):
        return self.questionlike_set.filter(value=-1).count()
    
class QuestionManager(models.Manager):
    def with_ratings(self):
        return self.annotate(
            like_count=Count('questionlike', filter=Q(questionlike__value=1)),
            dislike_count=Count('questionlike', filter=Q(questionlike__value=-1)),
            rating=Coalesce(Sum('questionlike__value'), 0)
        )

class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.question.title}"

    
class AnswerManager(models.Manager):
    def with_ratings(self):
        return self.annotate(
            like_count=Count('answerlike', filter=Q(answerlike__value=1)),
            dislike_count=Count('answerlike', filter=Q(answerlike__value=-1)),
            rating=Coalesce(Sum('answerlike__value'), 0)
        )
    
class Answer(models.Model):
    text = models.TextField(max_length=2000)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    
    objects = AnswerManager()

    def __str__(self):
        return f"Answer to {self.question.title}"

    def likes_count(self):
        return self.answerlike_set.filter(value=1).count()
    
    def dislikes_count(self):
        return self.answerlike_set.filter(value=-1).count()
    
class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.SmallIntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])

    class Meta:
        unique_together = ('answer', 'user')

    def __str__(self):
        return f"{self.user.username} likes answer #{self.answer.id}"