from django import forms

from nautobot.core.forms import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    add_blank_choice,
)
from nautobot.core.forms import (
    BootstrapMixin,
    BulkEditForm,
    BulkEditNullBooleanSelect,
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    JSONField,
    SlugField,
)
from nautobot.extras.forms import (
    NautobotBulkEditForm,
    NautobotModelForm,
    NautobotFilterForm,
)
from nautobot.extras.forms.mixins import (
    NoteModelBulkEditFormMixin,
    NoteModelFormMixin,
    RelationshipModelFormMixin,
)

from nautobot.dcim.models import Location
from nautobot.extras.models import Status, Tag, SecretsGroup
from nautobot.extras.datasources import get_datasource_content_choices

from .models import CdnSite, SiteRole, HyperCacheMemoryProfile, RedirectMapContext, RedirectMapContextSchema, CdnGitRepository


class HyperCacheMemoryProfileForm(NautobotModelForm):
    class Meta:
        model = HyperCacheMemoryProfile
        fields = [
            'name',
            'description',
            'hotCacheMemoryPercent',
            'ramOnlyCacheMemoryPercent',
            'diskIndexMemoryPercent',
            'frontEndCacheMemoryPercent',
            'cacheMemoryProfileId',
        ]

class HyperCacheMemoryProfileFilterForm(NautobotFilterForm):
    model = HyperCacheMemoryProfile

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)

#
# Site Roles
#


class SiteRoleForm(NautobotModelForm):
    parent = DynamicModelChoiceField(queryset=SiteRole.objects.all(), required=False)

    class Meta:
        model = SiteRole
        fields = [
            "parent",
            "name",
            "description",
        ]


#
# CDN Sites
#


class CdnSiteForm(NautobotModelForm):
    cdn_site_role = DynamicModelChoiceField(queryset=SiteRole.objects.all(), required=False)
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
    comments = CommentField()

    class Meta:
        model = CdnSite
        fields = [
            'name',
            "status",
            'abbreviatedName',
            'bandwidthLimitMbps',
            'enableDisklessMode',
            'neighbor1',
            'neighbor1_preference',
            'neighbor2',
            'neighbor2_preference',
            'cacheMemoryProfileId',
            'siteId',
            'cdn_site_role',
            'location',
        ]


class CdnSiteBulkEditForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=CdnSite.objects.all(), widget=forms.MultipleHiddenInput)
    status = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
    location = DynamicModelChoiceField(queryset=Location.objects.all(), required=False)
    cdn_site_role = DynamicModelChoiceField(queryset=SiteRole.objects.all(), required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    cacheMemoryProfileId = forms.ModelChoiceField(required=False, queryset=HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor1_preference = forms.IntegerField(required=False, label="Neighbor Preference")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Secondary Site Neighbor")
    neighbor2_preference = forms.IntegerField(required=False, label="Neighbor Preference")

    class Meta:
        nullable_fields = [
            "location",
            "cdn_site_role",
            "cacheMemoryProfileId",
            "enableDisklessMode",
            "neighbor1",
            "neighbor2",
        ]



class CdnSiteFilterForm(NautobotFilterForm):
    model = CdnSite

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    bandwidthLimitMbps = forms.IntegerField(required=False, label="Site Bandwidth Limit")
    enableDisklessMode = forms.BooleanField(required=False, label="Site Disk Mode")
    cacheMemoryProfileId = DynamicModelChoiceField(required=False, queryset=HyperCacheMemoryProfile.objects.all(), label="Akamai Site Memory Profile ID")
    neighbor1 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Primary Site Neighbor")
    neighbor2 = DynamicModelChoiceField(required=False, queryset=CdnSite.objects.all(), label="Secondary Site Neighbor")
    cdn_site_role = DynamicModelMultipleChoiceField(required=False, queryset=SiteRole.objects.all())

class RedirectMapContextForm(BootstrapMixin, NoteModelFormMixin):
    locations = DynamicModelMultipleChoiceField(queryset=Location.objects.all(), required=False)
    cdnsites = DynamicModelMultipleChoiceField(queryset=CdnSite.objects.all(), required=False)
    cdn_site_roles = DynamicModelMultipleChoiceField(queryset=SiteRole.objects.all(), required=False)
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    data = JSONField(label="")

    class Meta:
        model = RedirectMapContext
        fields = "__all__"


class RedirectMapContextBulkEditForm(BootstrapMixin, NoteModelBulkEditFormMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=RedirectMapContext.objects.all(), widget=forms.MultipleHiddenInput)
    schema = DynamicModelChoiceField(queryset=RedirectMapContextSchema.objects.all(), required=False)
    weight = forms.IntegerField(required=False, min_value=0)
    is_active = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect())
    description = forms.CharField(required=False, max_length=100)

    class Meta:
        nullable_fields = [
            "description",
            "schema",
        ]


class RedirectMapContextFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Search")
    schema = DynamicModelChoiceField(queryset=RedirectMapContextSchema.objects.all(), to_field_name="slug", required=False)
    Location = DynamicModelMultipleChoiceField(queryset=Location.objects.all(), to_field_name="slug", required=False)
    cdnsite = DynamicModelMultipleChoiceField(queryset=CdnSite.objects.all(), to_field_name="slug", required=False)
    cdn_site_roles = DynamicModelMultipleChoiceField(queryset=SiteRole.objects.all(), to_field_name="slug", required=False)
    tag = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), to_field_name="slug", required=False)
    
#
# RedirectMap context schemas
#


class RedirectMapContextSchemaForm(NautobotModelForm):
    data_schema = JSONField(label="")

    class Meta:
        model = RedirectMapContextSchema
        fields = (
            "name",
            "description",
            "data_schema",
        )


class RedirectMapContextSchemaBulkEditForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=RedirectMapContextSchema.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, max_length=100)

    class Meta:
        nullable_fields = [
            "description",
        ]


class RedirectMapContextSchemaFilterForm(BootstrapMixin, forms.Form):
    q = forms.CharField(required=False, label="Search")
    
#
# Git repositories and other data sources
#


def get_git_datasource_content_choices():
    return get_datasource_content_choices("nautobot_cdn_models.cdngitrepository")


class PasswordInputWithPlaceholder(forms.PasswordInput):
    """PasswordInput that is populated with a placeholder value if any existing value is present."""

    def __init__(self, attrs=None, placeholder="", render_value=False):
        if placeholder:
            render_value = True
        self._placeholder = placeholder
        super().__init__(attrs=attrs, render_value=render_value)

    def get_context(self, name, value, attrs):
        if value:
            value = self._placeholder
        return super().get_context(name, value, attrs)


class CdnGitRepositoryForm(BootstrapMixin, RelationshipModelFormMixin):
    slug = SlugField(help_text="Filesystem-friendly unique shorthand")

    remote_url = forms.URLField(
        required=True,
        label="Remote URL",
        help_text="Only http:// and https:// URLs are presently supported",
    )

    secrets_group = DynamicModelChoiceField(required=False, queryset=SecretsGroup.objects.all())

    provided_contents = forms.MultipleChoiceField(
        required=False,
        label="Provides",
        choices=get_git_datasource_content_choices,
    )

    class Meta:
        model = CdnGitRepository
        fields = [
            "name",
            "slug",
            "remote_url",
            "branch",
            "secrets_group",
            "provided_contents",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.present_in_database:
            self.fields["slug"].widget.attrs["readonly"] = True

    def save(self, commit=True):
        instance = super().save(commit=commit)

        # TODO(jathan): Move sync() call out of the form and into the view. However, in v2 UI this
        # probably just goes away since UI views will be making API calls. For now, the user is
        # magically stored on the instance by the view code.
        if commit:
            # Set dryrun if that button was clicked in the UI, otherwise perform a normal sync.
            dry_run = "_dryrun_create" in self.data or "_dryrun_update" in self.data
            instance.sync(user=instance.user, dry_run=dry_run)

        return instance


class CdnGitRepositoryBulkEditForm(NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CdnGitRepository.objects.all(),
        widget=forms.MultipleHiddenInput(),
    )
    remote_url = forms.CharField(
        label="Remote URL",
        required=False,
    )
    branch = forms.CharField(
        required=False,
    )
    secrets_group = DynamicModelChoiceField(required=False, queryset=SecretsGroup.objects.all())

    class Meta:
        model = CdnGitRepository
        nullable_fields = ["secrets_group"]


class CdnGitRepositoryFilterForm(BootstrapMixin, forms.Form):
    model = CdnGitRepository
    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    branch = forms.CharField(required=False)
    provided_contents = forms.ChoiceField(
        required=False,
        label="Provides",
        choices=add_blank_choice(get_git_datasource_content_choices()),
    )