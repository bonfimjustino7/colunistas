# coding:utf-8
import os, zipfile

from django.db.models import Q
from django.contrib import admin, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.conf.urls import url
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from django.contrib.admin import helpers
from django.contrib.admin.utils import flatten_fieldsets
from django.forms.models import modelform_factory
from django import forms
from functools import partial
from io import StringIO

from datetime import datetime

from mptt.admin import DraggableMPTTAdmin
from ckeditor.widgets import CKEditorWidget
from poweradmin.admin import PowerModelAdmin, PowerButton

from .forms import ThemeForm, CustomGroupForm, PowerArticleForm

from .models import Menu, Section, Article, SectionItem, URLMigrate, \
    FileDownload, ArticleArchive, ArticleComment, \
    Theme, Permissao, GroupType, GroupItem, ArticleAttribute


class FileDownloadAdmin(PowerModelAdmin):
    list_display = ['title', 'file', 'count', 'expires_at']
    readonly_fields = ['count', 'download_url']
    fieldsets = (
        (None, {
            'fields': ['title', 'file', 'expires_at', 'create_article', 'count', 'download_url', ]
        }),
    )

    def get_buttons(self, request, object_id):
        buttons = super(FileDownloadAdmin, self).get_buttons(request, object_id)
        if object_id:
            obj = self.get_object(request, object_id)
            if obj.article:
                buttons.append(PowerButton(url=obj.article_url(), label='Artigo'))
        return buttons

    def save_model(self, request, obj, form, change):
        super(FileDownloadAdmin, self).save_model(request, obj, form, change)
        if obj.create_article and not obj.article:
            article = Article(
                title=u'Download %s' % obj.title,
                content=u'<a href="%s">Download</a>' % obj.get_absolute_url(),
                author=request.user,
            )
            article.save()
            obj.article = article
            obj.save()


admin.site.register(FileDownload, FileDownloadAdmin)


class URLMigrateAdmin(PowerModelAdmin):
    list_display = ['old_url', 'new_url', 'redirect_type', 'dtupdate', 'views']

    class Media:
        js = ('js/custom_admin.js', )


admin.site.register(URLMigrate, URLMigrateAdmin)


class SectionItemCreateInline(admin.TabularInline):
    model = SectionItem
    extra = 1

    def queryset(self, request):
        return super(SectionItemCreateInline, self).queryset(request).none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'article':
            kwargs['queryset'] = Article.objects.filter(is_active=True)
            return db_field.formfield(**kwargs)
        return super(SectionItemCreateInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SectionItemActiveInline(admin.TabularInline):
    model = SectionItem
    extra = 0
    readonly_fields = ['display_article_link', 'section', 'display_article_created_at']
    fields = ['display_article_link', 'section', 'order', 'display_article_created_at']

    def has_add_permission(self, request):
        return False


class PermissaoSectionInline(admin.TabularInline):
    model = Permissao
    extra = 1


class SectionAdmin(PowerModelAdmin):
    list_display = ['title', 'views', 'conversions', 'num_articles', 'order']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order', )
    multi_search = (
        ('q1', 'Título', ['title']),
        ('q2', 'Slug', ['slug']),
    )
    fieldsets_superuser = (
        (None, {
            'fields': ['title', 'slug', 'header', 'keywords', 'order', 'template', ]
        }),
    )
    fieldsets = (
        (None, {
            'fields': ['title', 'slug', 'header', 'keywords', 'order']
        }),
    )
    inlines = [SectionItemActiveInline, SectionItemCreateInline, PermissaoSectionInline]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return self.fieldsets_superuser
        return self.fieldsets

    def get_form(self, request, obj=None, **kwargs):
        defaults = {
            "form": self.form if not obj else forms.ModelForm,
            "fields": flatten_fieldsets(self.get_fieldsets(request, obj)),
            "exclude": self.get_readonly_fields(request, obj),
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['header']:
            kwargs['widget'] = CKEditorWidget()

        return super(SectionAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Section, SectionAdmin)


class GroupItemGroupTypeInline(admin.TabularInline):
    model = GroupItem
    extra = 1


class GroupTypeAdmin(PowerModelAdmin):
    list_display = ['name', 'order']
    search_fields = ('name', )
    list_editable = ('order', )
    fieldsets = (
        (None, {
            'fields': ['name', 'order', ]
        }),
    )
    inlines = [GroupItemGroupTypeInline, ]


admin.site.register(GroupType, GroupTypeAdmin)


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 0
    verbose_name_plural = u'Seções'


class ArticleAttributeInline(admin.TabularInline):
    model = ArticleAttribute
    extra = 1


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0
    fields = ('created_at', 'author', 'comment', 'active')
    readonly_fields = ('created_at', 'author', 'comment')


class ArticleAdmin(PowerModelAdmin):
    list_display = ('title', 'slug', 'get_sections_display', 'created_at', 'is_active', 'allow_comments', 'views', 'conversions', )
    list_editable = ('is_active', )
    date_hierarchy = 'created_at'
    multi_search = (
        ('q1', 'Título', ['title']),
        ('q2', 'Conteúdo', ['content']),
        ('q3', 'Slug', ['slug']),
    )
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {
            'fields': [
                ('title', 'slug'), 'header', 'content', 'keywords', 'created_at', 'author', 'is_active', 'allow_comments',
            ]
        }),
    )
    actions = ('reset_views', )
    inlines = (SectionItemInline, ArticleAttributeInline, ArticleCommentInline, )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['header', 'content']:
            kwargs['widget'] = CKEditorWidget()
        return super(ArticleAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['initial'] = request.user.id
            kwargs['queryset'] = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True))
            return db_field.formfield(**kwargs)
        return super(ArticleAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def clone(self, request, id):
        article_clone = Article.objects.get(pk=id)
        article_clone.pk = None
        article_clone.slug = None
        article_clone.views = 0
        article_clone.conversions = 0
        article_clone.created_at = datetime.now()
        article_clone.save()

        self.log_addition(request, article_clone, '')

        for si in SectionItem.objects.filter(article__pk=id):
            si_clone = SectionItem(
                section=si.section,
                article=article_clone,
                order=si.order
            )
            si_clone.save()
        return HttpResponseRedirect(reverse('admin:cms_article_change', args=(article_clone.id,)))

    def add_power_view(self, request, form_url='', extra_context=None):
        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        ModelForm = PowerArticleForm
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES)
            if form.is_valid():
                new_object = self.save_form(request, form, change=False)
                self.save_model(request, new_object, form, False)
                for section in form.cleaned_data.get('sections'):
                    SectionItem(section=section, article=new_object).save()
                self.log_addition(request, new_object, '')
                return self.response_add(request, new_object)
        else:
            form = ModelForm()

        fieldsets = (
            (None, {
                'fields': ['title', 'content', 'sections']
            }),
        )
        adminForm = helpers.AdminForm(form, list(fieldsets), {}, [], model_admin=self)
        media = self.media + adminForm.media

        context = {
            'title': u'Adicionar Artigo',
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': [],
            'errors': helpers.AdminErrorList(form, []),
            'app_label': opts.app_label,
        }
        context.update(extra_context or {})
        return self.render_change_form(request, context, form_url=form_url, add=True)

    def get_urls(self):
        urls = super(ArticleAdmin, self).get_urls()
        return [
            url(r'^add-power/$', self.wrap(self.add_power_view), name='cms_article_add_power'),
            url(r'^clone/(?P<id>\d+)/$', self.wrap(self.clone), name='cms_article_clone'),
        ] + urls

    def get_buttons(self, request, object_id):
        buttons = super(ArticleAdmin, self).get_buttons(request, object_id)
        if object_id:
            buttons.append(PowerButton(url=reverse('admin:cms_article_clone', args=(object_id, )), label='Duplicar Artigo'))
            buttons.append(PowerButton(url="%s?article__id__exact=%s" % (reverse('admin:cms_articlearchive_changelist'), object_id), label='Versões'))
        return buttons

    def reset_views(self, request, queryset):
        num_oper = 0
        for rec in queryset:
            rec.views = 0
            rec.conversions = 0
            rec.save()
            num_oper += 1
        self.message_user(request, 'Artigos reiniciados: %d ' % num_oper)
    reset_views.short_description = u'Apagar número de visualizações e conversões'

    def save_model(self, request, obj, form, change):
        # Versionamento
        if change:
            ant = Article.objects.get(pk=obj.pk)
            version = ArticleArchive(
                article=obj,
                user=request.user
            )
            if ant.header != obj.header:
                version.header = obj.header
                version.save()
            if ant.content != obj.content:
                version.content = obj.content
                version.save()

        if not change:
            obj.author = request.user
            obj.save()

            # Versionamento
            ArticleArchive.objects.create(
                article=obj,
                header=obj.header,
                content=obj.content,
                user=request.user
            )
        return super(ArticleAdmin, self).save_model(request, obj, form, change)


admin.site.register(Article, ArticleAdmin)


class ArticleArchiveAdmin(PowerModelAdmin):
    list_display = ['article', 'updated_at', 'user', ]
    list_filter = ['article', 'updated_at', ]
    multi_search = (
        ('q1', 'Título', ['article__title']),
        ('q2', 'Conteúdo', ['content']),
    )
    readonly_fields = ['article', 'user', 'updated_at', ]

    fieldsets = (
        (None, {
            'fields': ['article', 'user', 'updated_at', 'header', 'content', ]
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ['header', 'content']:
            kwargs['widget'] = CKEditorWidget()
        return super(ArticleArchiveAdmin, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(ArticleArchive, ArticleArchiveAdmin)


class MenuAdmin(DraggableMPTTAdmin):
    list_display = ('indented_title', 'is_active', 'tree_actions',)
    list_display_links = ('indented_title', )

    list_editable = ('is_active', )


admin.site.register(Menu, MenuAdmin)


class ThemeAdmin(PowerModelAdmin):
    list_display = ('name', 'example', 'active',)
    multi_search = (
        ('q1', u'Nome', ['name']),
        ('q2', u'Descrição', ['description']),
    )
    fieldsets_add = (
        (None, {'fields': ['name', 'active', 'description', ]}),
        (u'Arquivo', {'fields': ['path_name', 'theme', ]}),
    )
    fieldsets_edit = (
        (None, {'fields': ['name', 'active', 'description', ]}),
        (u'Arquivos', {'fields': ['treepath', ]}),
    )
    form = ThemeForm

    def get_actions(self, request):
        return []

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return ('name', 'treepath', )
        self.prepopulated_fields = {'path_name': ('name',)}
        return super(ThemeAdmin, self).get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.fieldsets_add
        return self.fieldsets_edit

    def get_form(self, request, obj=None, **kwargs):
        defaults = {
            "form": self.form if not obj else forms.ModelForm,
            "fields": flatten_fieldsets(self.get_fieldsets(request, obj)),
            "exclude": self.get_readonly_fields(request, obj),
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.active:
            return False
        return super(ThemeAdmin, self).has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if obj.active:
            Theme.objects.exclude(pk=obj.pk).update(active=False)
        return super(ThemeAdmin, self).save_model(request, obj, form, change)

    def backup(self, request, object_id):
        theme = get_object_or_404(Theme, pk=object_id)
        try:
            buffer = StringIO.StringIO()
            zip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)

            for root, dirs, files in os.walk(theme.path):
                for file in files:
                    zip.write(os.path.join(root, file), os.path.join(root.replace(theme.path, theme.path_name.strip()), file))

            zip.close()
            buffer.flush()
            ret_zip = buffer.getvalue()
            buffer.close()
            response = HttpResponse(ret_zip, content_type='application/octet-stream')
            response['Content-Disposition'] = 'filename=%s.zip' % theme.path_name.replace('/', '')
            return response
        except Exception:
            messages.error(request, u'Erro ao criar .zip do tema!')
            return HttpResponseRedirect(reverse('admin:cms_theme_change', args=(object_id,)))

    def get_urls(self):
        urls = super(ThemeAdmin, self).get_urls()
        return [
            url(r'^backup/(?P<object_id>\d+)/$', self.wrap(self.backup), name='cms_theme_backup'),
        ] + urls

    def get_buttons(self, request, object_id):
        buttons = super(ThemeAdmin, self).get_buttons(request, object_id)
        if object_id:
            obj = self.get_object(request, object_id)
            buttons.append(PowerButton(url='%s?&dir=%s' % (reverse('filebrowser:fb_browse'), obj.media_path()), label=u'Editar'))
            buttons.append(PowerButton(url=reverse('admin:cms_theme_backup', kwargs={'object_id': object_id, }), label=u'Backup'))
        return buttons


admin.site.register(Theme, ThemeAdmin)


# ## Nova tela do Group ###
admin.site.unregister(Group)


class GroupAdminCustom(PowerModelAdmin, GroupAdmin):
    form = CustomGroupForm


admin.site.register(Group, GroupAdminCustom)


# ## Nova tela do usuário ###
admin.site.unregister(User)


class UserAdminCustom(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'groups',)
    readonly_fields = ('last_login', 'date_joined',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions', )

    fieldsets_user = (
        (None, {'fields': ('username', 'password')}),
        (u'Informações pessoais', {'fields': ('first_name', 'last_name', 'email', )}),
        (u'Permissões', {'fields': ('is_active', 'is_staff', 'groups', )}),
        (u'Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    fieldsets_superuser = (
        (None, {'fields': ('username', 'password')}),
        (u'Informações pessoais', {'fields': ('first_name', 'last_name', 'email', )}),
        (u'Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', )}),
        (u'Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            return self.fieldsets_superuser
        return self.fieldsets_user


admin.site.register(User, UserAdminCustom)