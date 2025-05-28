from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from app.models import Answer, Question

def setRightAnswerResponse(request, answer_id):
    if request.method == "POST":
        question_id = request.POST.get("question")
        is_correct = request.POST.get("is_correct", "").lower() == 'true'
        
        question = get_object_or_404(Question, id=question_id)
        answer = get_object_or_404(Answer, id=answer_id, question=question)

        if question.author != request.user:
            return JsonResponse({"error": "Not author of question"}, status=403)

        if answer.is_correct and not is_correct:
            answer.is_correct = False
            answer.save()
            return JsonResponse({
                "is_correct": False,
            })
        
        if not answer.is_correct and is_correct:
            Answer.objects.filter(question=question).update(is_correct=False)
            answer.is_correct = True
            answer.save()
            return JsonResponse({
                "is_correct": True
            })
        
        return JsonResponse({
            "is_correct": answer.is_correct
        })
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)