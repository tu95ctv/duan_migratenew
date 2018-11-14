from unidecode  import unidecode
import json
from openerp.http import request

def download_by_url(model,id,kw,pick_func):
    active_domain = kw['active_domain']
    active_domain = active_domain.replace("'",'"')
    active_domain = json.loads(active_domain)
    dj_obj = request.env['downloadwizard.download'].browse(int(id))
    call_func = pick_func[model]
    workbook,name = call_func(dj_obj,active_domain)
    name = unidecode(name).replace(' ','_')
    response = request.make_response(None,
        headers=[('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', 'attachment; filename=%s;target=blank' %name)],
        )
    workbook.save(response.stream)
    return response