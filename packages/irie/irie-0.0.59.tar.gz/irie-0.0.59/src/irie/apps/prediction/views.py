#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
#   This module implements the "Configure Predictors" page
#
#   Author: Claudio Perez
#
#----------------------------------------------------------------------------#
import os
import json
import veux
import uuid
import base64
import hashlib

from django.template import loader
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.shortcuts import HttpResponse, get_object_or_404

from irie.apps.inventory.models import Asset
from irie.apps.prediction.predictor import PREDICTOR_TYPES
from irie.apps.prediction.models import PredictorModel
from .forms import PredictorForm


def _get_asset(calid, request):
    # TODO: Implement this like get_object_or_404 and move under apps.inventory
    try:
        return Asset.objects.get(calid=calid)

    except Asset.DoesNotExist:
        context = {
            "segment": "assets"
        }
        return HttpResponse(
                loader.get_template("site/page-404-sidebar.html").render(context, request)
        )


@login_required(login_url="/login/")
def asset_predictors(request, calid):
    html_template = loader.get_template("prediction/asset-predictors.html")

    context = {
        "segment": "assets"
    }

    context["runners"] = list(reversed([
        {
            "schema": json.dumps(cls.schema),
            "name":   cls.__name__,
            "title":  cls.schema.get("title", "NO TITLE"),
            "protocol":   key
        }
        for key,cls in PREDICTOR_TYPES.items() if key
    ]))


    try:
        context["asset"] = Asset.objects.get(calid=calid)

    except Asset.DoesNotExist:
        return HttpResponse(
                loader.get_template("site/page-404-sidebar.html").render(context, request)
               )

    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def predictor_render(request, calid, preid):

    predictor = get_object_or_404(PredictorModel, pk=int(preid))
    
    sname = request.GET.get("section", None)

    runner = PREDICTOR_TYPES[predictor.protocol](predictor) 

    try:
        _, mesh = runner.structural_section(sname)

        can = veux._create_canvas(name="gltf")
        import numpy as np
        R = np.array([[1, 0],[0, 1], [0, 0]])
        can.plot_lines(mesh.exterior()@R.T)
        if (interior := mesh.interior()) is not None:
            for i in interior:
                can.plot_lines(i@R.T)
        glb = can.to_glb()
        return HttpResponse(glb, content_type="application/binary")

    except Exception as e:
        return HttpResponse(
            json.dumps({"error": "Section not found"}),
            content_type="application/json",
            status=404
        )


@login_required(login_url="/login/")
def predictor_profile(request, calid, preid):

    def _string_to_id(s: str) -> str:
        """Convert a string to a URL-safe identifier."""
        # 1. SHA-256 into bytes   
        # 2. URL-safe Base64 (no + / =)   
        # 3. strip padding
        b64 = base64.urlsafe_b64encode(
                hashlib.sha256(s.encode()).digest()
            ).rstrip(b'=').decode('ascii')
        return f"id_{b64}"


    context = {
        "segment": "assets",
    }

    asset = get_object_or_404(Asset, calid=calid)

    predictor = get_object_or_404(PredictorModel, pk=int(preid))

    context["asset"] = asset
    context["runner"] = PREDICTOR_TYPES[predictor.protocol](predictor)
    context["predictor"] = predictor
    context["sensors"]   = predictor.sensorassignment_set.all()

    try:
        if predictor.protocol == PredictorModel.Protocol.TYPE1:
            html_template = loader.get_template("prediction/xara-profile.html")
            
            context["members"] = context["runner"].structural_members()

            context["sections"] = [
                {
                    "id": _string_to_id(name),
                    "name": name,
                } for _, name in context["runner"].structural_sections()
            ]

        else:
            html_template = loader.get_template("prediction/predictor-profile.html")

        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def asset_map(request, calid):
    """
    See also https://www.f4map.com/
    """
    r200 = loader.get_template("inventory/asset-on-map.html")
    r400 = loader.get_template("site/page-400.html")
    asset = Asset.objects.get(calid=calid)
    context = {
        "asset": asset,
        "viewer": "three",
        "location": json.dumps(list(reversed(list(asset.coordinates)))),
    }

    if request.method == "GET":
        context["render_src"] = asset.rendering

    elif request.method == "POST":
        # context["offset"] = json.dumps(list(reversed(list(asset.coordinates))))
        context["rotate"] = "[0, 0, 0]"
        context["scale"]  = 1/3.2808 # TODO

        uploaded_file = request.FILES.get('config_file')

        from openbim.csi import load, create_model, collect_outlines
        try:
            csi = load((str(line.decode()).replace("\r\n","\n") for line in uploaded_file.readlines()))
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=400)

        try:
            model = create_model(csi, verbose=True)
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=400)


        outlines = collect_outlines(csi, model.frame_tags)
        artist = veux.render(model, canvas="gltf", vertical=3,
                                reference={"frame.surface", "frame.axes"},
                                model_config={"frame_outlines": outlines})

        glb = artist.canvas.to_glb()
        glb64 = base64.b64encode(glb).decode("utf-8")
        context["render_glb"] = f"data:application/octet-stream;base64,{glb64}"


    try:
        return HttpResponse(r200.render(context, request))

    except Exception as e:
        raise e
        r500 = loader.get_template("site/page-500.html")
        return HttpResponse(r500.render({"message": str(e)}, request), status=500)



@login_required(login_url="/login/")
def create_mdof(request):
    "Create system id"
    context = {}

    page_template = "create-mdof.html"
    context["segment"] = page_template
    html_template = loader.get_template("prediction/" + page_template)
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def create_model(request, calid):

    asset = Asset.objects.get(calid=calid)
    html_template = loader.get_template("prediction/create-model.html")
    r400 = loader.get_template("site/page-400.html")
    context = {
        "asset": asset,
        "segment": "assets",
        "viewer": "three",
        "offset": json.dumps(list(reversed(list(asset.coordinates)))),
    }

    if request.method == "POST":
        form = PredictorForm(request.POST, request.FILES)

        uploaded_file = request.FILES.get('config_file')

        from xcsi.csi import load, create_model, collect_outlines
        # 1) Parse the CSI file
        try:
            csi = load((str(line.decode()).replace("\r\n","\n") for line in uploaded_file.readlines()))
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=500)

        # 2) Process CSI data into xara model
        try:
            model = create_model(csi, verbose=True)
        except Exception as e:
            return HttpResponse(r400.render({"message": json.dumps({"error": str(e)})}), status=500)

        # 3) Render the model
        outlines = collect_outlines(csi, model.frame_tags)
        artist = veux.create_artist(model,
                                    canvas="gltf",
                                    vertical=3,
                                    model_config={"frame_outlines": outlines}
        )
        artist.draw_surfaces()

        # Generate the rendering .glb
        glb = artist.canvas.to_glb()

        if request.POST.get("action") == "commit":
            if not form.is_valid():
                return HttpResponse(json.dumps({"error": "Invalid form data"}), status=400)
            predictor = PredictorModel()
            predictor.active = False
            predictor.asset = asset
            predictor.name = form.cleaned_data['name']
            predictor.description = "empty"
            predictor.protocol = PredictorModel.Protocol.TYPE1

            predictor.config_file.save(uploaded_file.name, ContentFile(uploaded_file.read()), save=True)
            predictor.render_file.save(f"{uuid.uuid4()}.glb", ContentFile(glb), save=True)
            predictor.save()

        context["form"] = form

    else: #  GET
        context["form"] = PredictorForm()


    try:
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        if "DEBUG" in os.environ and os.environ["DEBUG"]:
            raise e
        print(e)
        html_template = loader.get_template("site/page-500.html")
        return HttpResponse(html_template.render({}, request), status=500)


