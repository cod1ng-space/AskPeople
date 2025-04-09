# Время заполнения бд составило чуть меньше 6 минут
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Fill database with test data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Ratio for data generation')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']

        # Заполнение профилей и пользователей
        users = []
        for i in range(ratio):
            user = User(
                username=fake.unique.user_name(),

                email=fake.email(),
                password='password123'
            )
            users.append(user)
            if i % 1000 == 0:
                self.stdout.write(f'Created {i} users')
        self.stdout.write(f'Created {ratio} users')

        User.objects.bulk_create(users)
        Profile.objects.bulk_create([Profile(user=user) for user in users])
        fake.unique.clear()

        # Заполнение тегов
        tags = []
        generated_names = set()
        for i in range(ratio):

            while True:
                name = '-'.join(fake.words(nb=2))
                if len(name) <= 30 and name not in generated_names:
                    generated_names.add(name)
                    break
            tag = Tag(
                name=name,
                color=random.choice(["pri", "sec", "suc", "dan", "war", "inf", "lig", "dar"])
            )
            tags.append(tag)
            if i % 1000 == 0:
                self.stdout.write(f'Created {i} tags')
        self.stdout.write(f'Created {ratio} tags')

        Tag.objects.bulk_create(tags)
        fake.unique.clear()

        # Заполнение вопросов
        questions = []
        for i in range(ratio * 10):
            question = Question(
                title=fake.sentence()[:-1] + '?',
                text=fake.text(),
                author=random.choice(users)
            )
            questions.append(question)
            if i % 10000 == 0:
                self.stdout.write(f'Created {i} questions')
        self.stdout.write(f'Created {ratio * 10} questions')

        Question.objects.bulk_create(questions)
        
        # Добавляем теги к вопросам
        tag_ids = list(Tag.objects.values_list('id', flat=True))
        for question in questions:
            question.tags.set(random.sample(tag_ids, min(3, len(tag_ids))))

        # Заполнение ответов
        answers = []
        question_ids = list(Question.objects.values_list('id', flat=True))
        for i in range(ratio * 100):
            answer = Answer(
                text=fake.text(),
                question_id=random.choice(question_ids),
                author=random.choice(users)
            )
            answers.append(answer)
            if i % 100000 == 0:
                self.stdout.write(f'Created {i} answers')
        self.stdout.write(f'Created {ratio * 100} answers')
        Answer.objects.bulk_create(answers)

        # Заполнение лайков к вопросам
        question_likes = []
        existed_question_pairs = set() 
        for i in range(ratio * 200):
            while True:
                question = random.choice(questions)
                user = random.choice(users)
                pair = (question.id, user.id)
                if pair not in existed_question_pairs:
                    existed_question_pairs.add(pair)
                    break
            
            question_likes.append(QuestionLike(
                question=question,
                user=user,
                value=random.choice([1, -1])
            ))
            if i % 100000 == 0:
                self.stdout.write(f'Created {i}|{ratio * 200} question likes')
        self.stdout.write(f'Created {ratio * 200}|{ratio * 200} question likes')
        QuestionLike.objects.bulk_create(question_likes)

        # Заполнение лайков к ответам
        answer_likes = []
        existed_answer_pairs = set() 
        for i in range(ratio * 200):
            while True:
                answer=random.choice(answers)
                user=random.choice(users)
                pair = (answer.id, user.id)
                value=random.choice([1, -1])
                if pair not in existed_answer_pairs:
                    existed_answer_pairs.add(pair)
                    break
            
            answer_likes.append(AnswerLike(
                answer=answer,
                user=user,
                value=value,
            ))
            if i % 100000 == 0:
                self.stdout.write(f'Created {i}|{ratio * 200} answer likes')
        self.stdout.write(f'Created {ratio * 200}|{ratio * 200} answer likes')
        AnswerLike.objects.bulk_create(answer_likes)

        self.stdout.write(self.style.SUCCESS(f'Successfully filled database with ratio {ratio}'))
        self.stdout.write(self.style.SUCCESS('\nActual database counts:'))
        self.stdout.write(self.style.SUCCESS(f'- Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Profiles: {Profile.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Tags: {Tag.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Questions: {Question.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- Answers: {Answer.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- QuestionLikes: {QuestionLike.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'- AnswerLikes: {AnswerLike.objects.count()}'))