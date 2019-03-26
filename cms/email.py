# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template.context import Context

from threading import Thread
from time import sleep


# Envia email
def sendmail(subject='', to=[], params={}, template='', mimetype='text/html; charset=UTF-8', headers={}):
    from .models import Recurso
    ativo = Recurso.objects.get_or_create(recurso='EMAIL')[0].ativo
    headers.update({'Reply-To': settings.REPLY_TO_EMAIL, })
    '''
    Método para envio de e-mail:
    - subject: string contendo assunto do e-mail
    - to: lista dos e-mails dos destinatários
    - params: dicionário com os parâmetros para renderizar o e-mail
    - template: string para o caminho do template do e-mail
    - mimetype: string de tipo e charset do arquivo de e-mail, padrão 'text/html; charset=UTF-8'
    '''
    def send_thread_email(subject='', to=[], params={}, template='', mimetype='', headers={}):
        from .models import EmailAgendado
        email = EmailAgendado.objects.create(
            subject=subject,
            to=list(to)
        )

        text_content = subject
        template_content = get_template(template)
        if template_content:
            html_content = template_content.render(Context(params))
            email.html = html_content
        else:
            email.html = u'Erro ao criar HTML.'
        email.save()

        '''
                try:
                    template_content = get_template(template)
                except:
                    try:
                        template_content = Template(template)
                    except:
                        email.html = u'Erro ao criar HTML.'
                        email.status = 'E'
                        email.save()

                        try:
                            #Enviar email para os administradores.
                            error_message = """
                                Erro ao criar HTML para email.<br>
                                <b>DADOS</b><br>
                                <b>to:</b> %s<br>
                                <b>template:</b> %s<br>
                                <b>params:</b> %s<br>
                                <b>e-mail:</b>%s%s<br>
                            """ % (to, template, params, settings.SITE_URL, reverse('admin:cms_emailagendado_change', args=(email.pk, )) )
                            msg = EmailMultiAlternatives(
                                u'Erro ao criar HTML para email.',
                                error_message,
                                settings.DEFAULT_FROM_EMAIL,
                                bcc=[admin[1] for admin in settings.ADMINS]
                            )
                            msg.attach_alternative(error_message, mimetype)
                            msg.send()
                        except: pass
                        return
        '''

        tentativas = 0
        while tentativas < 3:
            try:
                if ativo:
                    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, bcc=to, headers=headers)
                    msg.attach_alternative(html_content, mimetype)
                    msg.send()
                    email.status = 'K'
                    email.save()
                    break
                else:
                    email.status = 'A'
                    email.save()
                    break
            except:
                tentativas += 1
                if tentativas < 3: email.status = 'R'
                else: email.status = 'E'
                email.save()
                sleep(60)

    th=Thread(target=send_thread_email, args=(subject, to, params, template, mimetype, headers))
    th.start()


def resendmail_email_agendado(email, mimetype='text/html; charset=UTF-8', headers={}):
    try:
        headers.update({'Reply-To': settings.REPLY_TO_EMAIL, })
        msg = EmailMultiAlternatives(email.subject, email.html, settings.DEFAULT_FROM_EMAIL, to=eval(email.to), headers=headers)
        msg.attach_alternative(email.html, mimetype)
        msg.send()
        email.status = 'K'
    except: email.status = 'E'
    email.save()
