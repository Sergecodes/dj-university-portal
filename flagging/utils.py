"""General purpose functions that provide utility throughout the application"""
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def get_content_type(model_obj):
    return ContentType.objects.get_for_model(model_obj.__class__)


def get_model_object(*, app_name, model_name, model_id):
    """
    Get content object.
    Args:
        app_name (str): name of the app that contains the model.
        model_name (str): name of the model class.
        model_id (int): the id of the model object.

    Returns:
        object: model object according to the parameters passed
    """
    content_type = ContentType.objects.get(app_label=app_name, model=model_name.lower())
    model_object = content_type.get_object_for_this_type(id=model_id)

    return model_object


def process_flagging_request(*, user, model_obj, data):
    """
    Process flagging request and return a response. This handles request for both Django and DRF

    Args:
        user ([type]): The looged in user
        model_obj ([type]): the object being flagged
        data (dict): the data received from the request

    Returns:
        [dict]: response has three keys:
            `status`(int): zero indicates the request failed due to `ValidationError`.
            `msg`(str): response, success message in case request succeeds, reason for
            failure if it doesn't.

            **This key will only be present when request succeeds.**
            `flag`(int): Non-Zero(1) indicates that flag is created.
    """
    # To avoid circular import errors
    FlagInstance = apps.get_model('flagging', 'FlagInstance')
    response = { 'status': 0, }  # 0 for failure, non-zero(1) for success 

    try:
        result = FlagInstance.objects.set_flag(user, model_obj, **data)
        created, msg = result.get('created'), result.get('msg', '')

        # if new flag(flag instance) was created
        if created:
            response['msg'] = _(
                'The content has been flagged successfully. '
                'A moderator will review it shortly.'
            )
            response['flag'] = 1
            response['status'] = 1
        else:
            # if flag instance was deleted
            if result.get('deleted'):
                response['msg'] = _('The content has been unflagged successfully.')
                response['status'] = 1
            # if flag instance wasn't created (say if user flagged his own post)
            else:
                response['msg'] = msg
    except ValidationError as e:
        response.update({ 'msg': e.messages })

    return response
