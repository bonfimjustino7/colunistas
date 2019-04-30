# -*- coding: utf-8 -*-
import random
from django.db import models
from django.db.models import signals
from django.conf import settings

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives


def create_token(num=30):
    token = ""
    for x in range(num):
        token += random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    return token


def token_age():
    try:
        return settings.SESSION_TOKEN_AGE
    except:
        return 60*48 # 48 horas


def valid_token(owner, tk, auto_remove = True):
    token = UserToken.objects.filter(owner = owner, token = tk)
    if token:
        if token[0].valid():
            if auto_remove:
                token[0].delete()
            return True
    return False


class UserToken(models.Model):
    token = models.CharField(max_length = 30, primary_key = True, default = create_token)
    owner = models.CharField(max_length = 30)
    date_created = models.DateTimeField(auto_now = True)

    def valid(self):
        if self.date_created+timedelta(minutes=token_age()) < datetime.now():
            return False
        return True

    def link(self):
        return '{}/novo-usuario/{}/'.format(
            settings.SITE_HOST,
            self.token,
        )

    def __str__(self):
        return self.token


def clean_usertoken_post_save(signal, instance, sender, created, **kwargs):
    # Sempre que um novo token é gerado, a rotina tenta apagar os expirados
    limite = datetime.now()-timedelta(minutes = token_age())
    cnt = UserToken.objects.filter(date_created__lt = limite).count()
    LogObject(UserToken, 'clean_usertoken: %d %s' % (cnt, limite))


signals.post_save.connect(clean_usertoken_post_save, sender = UserToken)


def LogObject(object, mensagem):
    user = User.objects.get_or_create(username='sys')[0]
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.pk,
        object_repr=u'%s' % object,
        action_flag=CHANGE,
        change_message=mensagem
    )


def LogError(rotina, exception):
    user = User.objects.get_or_create(username='sys')[0]
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(user).pk,
        object_id=user.pk,
        object_repr=u'%s' % rotina,
        action_flag=ADDITION,
        change_message=exception
    )


STATUS_EMAIL = (
    ("A", u"Aguardando envio manual..."),
    ("S", u"Enviando..."),
    ("R", u"Re-enviando"),
    ("E", u"Erro ao enviar"),
    ("K", u"Enviado"),
)


class EmailAgendado(models.Model):
    class Meta:
        ordering = ('-date', )

    subject = models.CharField(max_length=90, default="")
    status = models.CharField(max_length=1, choices=STATUS_EMAIL, default="S")
    date = models.DateTimeField(default=datetime.now)
    to = models.TextField()
    html = models.TextField()

    def send(self):
        try:
            headers.update({'Reply-To': settings.REPLY_TO_EMAIL, })
            msg = EmailMultiAlternatives(self.subject, self.html, settings.DEFAULT_FROM_EMAIL,
                                         to=self.to.split(','))
            msg.attach_alternative(self.html, 'text/html; charset=UTF-8')
            msg.send()
            self.status = 'K'
        except:
            self.status = 'E'
        self.save()

    def __unicode__(self):
        return u"%s" % self.id
