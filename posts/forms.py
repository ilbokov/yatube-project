from django.forms import ModelForm, Select, Textarea

from .models import Comment, Group, Post


class PostForm(ModelForm):
    class Meta:
        """ Метакласс формы создания нового поста. """

        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'group': Select(choices=Group.objects.all()),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'cols': 20, 'rows': 5}),
        }
