from django.urls import reverse
from nautobot.extras.plugins import TemplateExtension

class CdnSiteContent(TemplateExtension):
    model = "dcim.device"

    def detail_tabs(self):

        return [
            {
                "title": "DataDog Graph",
                "url": reverse("plugins:nautobot_cdn_models:device_detail_tab", kwargs={"pk": self.context["object"].pk}),
            },
        ]

template_extensions = [CdnSiteContent]