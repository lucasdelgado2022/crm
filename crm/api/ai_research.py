import json
import re

import frappe
import requests


@frappe.whitelist()
def investigar_organizacion(organization):
	"""Investiga una organizacion con IA (Anthropic) y registra los hallazgos
	como registros CRM Fact (origen=IA). La API key se lee de site config:
	  bench --site <site> set-config anthropic_api_key sk-ant-...
	"""
	if not frappe.has_permission("CRM Organization", "read"):
		frappe.throw("Sin permiso para leer organizaciones")

	key = frappe.conf.get("anthropic_api_key")
	if not key:
		frappe.throw(
			"Falta configurar la API key de Anthropic. En el server: "
			"bench --site <site> set-config anthropic_api_key sk-ant-..."
		)

	org = frappe.get_doc("CRM Organization", organization)
	contexto = (
		f"Empresa: {org.name}\n"
		f"Sitio web: {org.get('website') or 'N/D'}\n"
		f"Industria: {org.get('industry') or 'N/D'}\n"
		f"Pais/Territorio: {org.get('territory') or 'N/D'}"
	)

	prompt = (
		"Sos un analista comercial B2B para una empresa que vende software de ingenieria "
		"(CAD, CAE, PLM, simulacion, mineria) y servicios asociados. Investiga la siguiente empresa "
		"y devolve informacion util y accionable para un vendedor: a que se dedica, sector, tamano aproximado, "
		"presencia geografica, y posibles necesidades o encaje con software de ingenieria.\n\n"
		f"{contexto}\n\n"
		"Respondé UNICAMENTE con un JSON valido, sin texto adicional, con esta forma exacta: "
		'{"resumen": "parrafo breve", "hechos": [{"hecho": "dato concreto y accionable", "fuente": "url o breve descripcion de la fuente"}]}. '
		"Maximo 6 hechos. Todo en espanol. Si no tenes informacion confiable, deja hechos como lista vacia."
	)

	payload = {
		"model": "claude-sonnet-5",
		"max_tokens": 1500,
		"messages": [{"role": "user", "content": prompt}],
	}
	headers = {
		"x-api-key": key,
		"anthropic-version": "2023-06-01",
		"content-type": "application/json",
	}

	try:
		r = requests.post(
			"https://api.anthropic.com/v1/messages",
			headers=headers,
			data=json.dumps(payload),
			timeout=120,
		)
	except Exception as e:
		frappe.throw("No se pudo contactar a la API de IA: " + str(e)[:200])

	if r.status_code != 200:
		frappe.throw("Error de la API de IA (%s): %s" % (r.status_code, r.text[:300]))

	data = r.json()
	text = ""
	for block in data.get("content", []):
		if block.get("type") == "text":
			text += block.get("text", "")

	parsed = {}
	m = re.search(r"\{.*\}", text, re.S)
	if m:
		try:
			parsed = json.loads(m.group(0))
		except Exception:
			parsed = {}

	resumen = (parsed.get("resumen") if isinstance(parsed, dict) else "") or text[:800]
	hechos = parsed.get("hechos") if isinstance(parsed, dict) else []
	if not isinstance(hechos, list):
		hechos = []

	creados = 0
	for h in hechos:
		if not isinstance(h, dict):
			continue
		texto = (h.get("hecho") or "").strip()
		if not texto:
			continue
		frappe.get_doc(
			{
				"doctype": "CRM Fact",
				"organization": organization,
				"hecho": texto,
				"fuente": (h.get("fuente") or "").strip(),
				"origen": "IA",
			}
		).insert(ignore_permissions=True)
		creados += 1

	frappe.db.commit()
	return {"resumen": resumen, "creados": creados}
