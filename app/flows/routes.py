from flask import render_template

from app.flows import bp
from app.dbapi import get_flow


@bp.route('/<flow_name>')
def show_flow(flow_name):
    flow = get_flow(flow_name)
    if not flow:
        return render_template('flows/404.html')

    return render_template(
        'flows/index.html',
        flow_name=flow_name,
        flow_post_count=flow['post_count'],
    )
