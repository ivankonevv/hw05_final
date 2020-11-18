from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {
            'group': 'Имя группы',
            'text': 'Текст записи',
            'image': 'Изображение',
        }
        help_texts = {
            'group': 'Выберите группу из списка',
            'text': 'Введите текст записи',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {"text": "Комментарий"}
        widgets = {
            "text": forms.Textarea(attrs={"rows": 2}),
        }
