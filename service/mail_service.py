import base64
import datetime
from glob import glob
import os
import httpx
import aiofiles


class SendMailService:
    def __init__(self, access_token: str, sendmail_url: str, root: str = "downloads"):
        self.root = root
        self.access_token = access_token
        self.sendmail_url = sendmail_url
        self.body_mail = ""

    async def send_mail(destinatarios: list[str], terminal: str, area_marinha: str):
        data = datetime.datetime.now().strftime("%d-%m-%Y")

        SendMailService.set_body(terminal, area_marinha)

        mail_dict = {
            "message": {
                "subject": f"Boletim Meteorológico {terminal} - {data}",
                "body": {
                    "contentType": "html",
                    "content": SendMailService.body_mail.replace("\n", ""),
                },
                "toRecipients": [{"emailAddress": {"address": d}} for d in destinatarios],
                "attachments": SendMailService.add_attachment(terminal),
            }
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                SendMailService.sendmail_url,
                headers={
                    "Authorization": f"Bearer {SendMailService.access_token}",
                    "Content-Type": "application/json",
                },
                json=mail_dict,
            )

        if response.status_code == 202:
            return "Email enviado com sucesso!"
        else:
            raise ValueError(
                f"Falha ao enviar o email. Código de status: {response.status_code}, Erro: {response.text}"
            )

    def set_body(terminal: str, area_marinha: str):
        SendMailService.body_mail = f"""
        <div>
            <p>TERMINAL {terminal.upper()} - Área Marinha {area_marinha.replace("ÁREA", "")}</p>
            <br><br>
            <p>
                <b>
                    <span style="color:red">ATENÇÃO:</span> 
                    Os documentos do Centro de Hidrografia da Marinha do Brasil em anexo são os mais recentes disponibilizados no website. 
                    <br>Para análise das informações atentar para as datas indicadas nos documentos.
                </b>
            </p>
            <br><br>
        </div>
        """

    async def get_list_anexos(self, terminal: str) -> str:
        list_path = os.path.join(self.root, terminal, "list.anexo")

        async with aiofiles.open(list_path, encoding="UTF-8") as f:
            linhas = await f.readlines()

        list_anexos = [
            f'<li><a href="{linha.split(";")[-1].strip()}">{linha.split(";")[0]}</a></li>'
            for linha in linhas
        ]

        return f"<h4>Links Utilizados:</h4><ul>{''.join(list_anexos)}</ul>"

    def add_attachment(self, terminal: str) -> list[dict]:
        files = glob(os.path.join(self.root, terminal, "*"))
        attachments = []

        for filepath in files:
            filename = os.path.basename(filepath)
            name, ext = os.path.splitext(filename)
            ext = ext.lower().lstrip(".")

            if ext not in {"txt", "anexo"}:
                content_type = {
                    "pdf": "application/pdf",
                    "png": "image/png",
                    "jpeg": "image/jpeg",
                    "jpg": "image/jpeg",
                }.get(ext, "application/octet-stream")

                with open(filepath, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")

                attachments.append({
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": filename,
                    "contentType": content_type,
                    "contentBytes": encoded,
                })

        return attachments
