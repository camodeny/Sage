from flask import Blueprint, render_template, request, render_template, url_for
import json
from supabase import create_client

client = create_client('https://mozvfpurociylfmytktl.supabase.co/', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1venZmcHVyb2NpeWxmbXl0a3RsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyNDk5MzM4MiwiZXhwIjoyMDQwNTY5MzgyfQ.22S0jzHGSKvpENiH1lQL-Rn1X68-R3ULmIPps6FrWCo')

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/confirm_email')
def confirm_email():
    return render_template('confirm_email.html')

@auth_bp.route('/signup')
def signup():
    return render_template('signup.html')

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/auth/verity_login', methods=['POST'])
def verity_login():
    token = request.json['token']
    if (token == None):
        return json.dumps({'status': 'error', 'message': 'No token provided'})
    try:
        response = client.auth.get_user(token)
    except Exception as e:
        return json.dumps({'status': 'error', 'message': "unknown token"})
        
    user = response.user
    if (not user):
        return json.dumps({'status': 'error', 'message': response.error})
    
    if (not user.user_metadata['email_verified']):
        return json.dumps({'status': 'success', 'message': 'email_not_verified'})

    response = client.table('users').select('id').eq('uuid', user.id).execute()
    if (response.count == None):
        client.table('users').insert({'uuid': user.id, 'name': user.user_metadata['name']}).execute()

    scripts = []
    for script in request.json['scripts']:
        scripts.append(url_for('static', filename=script))

    return json.dumps({'status': 'success', 'message': user.id, 'html': render_template(request.json['html_page']), 'scripts': scripts})