from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from version_control.mixins import AdminSiteView
from version_control.models import ModelObjectVersionGroup


class VCSRelationTreeUpdateView(AdminSiteView):
    """
    View for updating the version group relationship tree
    """

    template_name = "admin/version_control/modelobjectversiongroup/vcs_relation_tree.html"

    def get(self, request, *args, **kwargs):
        vcs_group = get_object_or_404(ModelObjectVersionGroup, pk=self.kwargs.get("pk"))
        vcs_group.update_vcs_relation_tree()
        context = dict(original=vcs_group)
        data = dict(template=render_to_string(self.template_name, context, request))
        return JsonResponse(data=data)
