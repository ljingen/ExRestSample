# -*- coding:utf-8 -*-
# snippets.models.py
from datetime import datetime

from django.db import models
from pygments.lexers import get_all_lexers, get_lexer_by_name   # 一个实现代码高亮的模块
from pygments.styles import get_all_styles
from pygments import highlight
from pygments.formatters.html import HtmlFormatter


# Create your models here.

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])  # 得到所有编程语言的选项
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())  # 列出所有配色风格


class Snippet(models.Model):
    owner = models.ForeignKey('auth.User', related_name='snippets',blank=True, null=True)
    highlighted = models.TextField()
    created = models.DateTimeField(default=datetime.now, verbose_name=u'创建时间')
    title = models.CharField(max_length=100, blank=True, default='', verbose_name=u'标题')
    code = models.TextField(verbose_name=u'代码块')
    linenos = models.BooleanField(default=False, verbose_name=u'一行')
    language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default='python', verbose_name=u'选择语言')
    style = models.CharField(max_length=100, choices=STYLE_CHOICES, default='friendly', verbose_name=u'样式')

    class Meta:
        ordering = ['created']
        verbose_name = u'代码段'
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        """
        使用pygments来创建高亮的HTML代码。
        """
        lexer = get_lexer_by_name(self.language)
        linenos = self.linenos and 'table' or False
        options = self.title and {'title':self.title} or {}
        formatter = HtmlFormatter(style=self.style, linenos=linenos, full =True, **options)
        self.highlighted = highlight(self.code, lexer, formatter)
        super(Snippet,self).save(*args, **kwargs)
