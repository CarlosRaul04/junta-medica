# Despliegue en AWS (para la presentación)

Objetivo: la aplicación web funcionando en internet **solo el tiempo necesario** (probar y presentar) y luego
**borrar todo** para no pagar. La cuenta del equipo no tiene créditos: se paga por hora (menos de 1 USD por día de uso).

**Base de datos: MongoDB** (recomendación del profesor). Usuarios e historial de consultas se guardan como
documentos en las colecciones `users` y `consultations`; los informes PDF y el resultado completo de cada junta (JSON)
van a **S3**.

```
Navegador ──► EC2 (Ubuntu 24.04, t3.medium)
                 ├── app Streamlit + agentes + búsqueda en guías (ChromaDB)
                 ├── MongoDB 8.0  (solo escucha dentro del servidor: no es accesible desde internet)
                 └──► S3 (con el rol IAM del servidor, sin claves): resultados JSON e informes PDF
```

El código no cambia: en el `.env` del servidor se pone `STORAGE_BACKEND=aws`, `MONGODB_URI` y `S3_BUCKET`
(ver `factories/storage_factory.py`). En la PC de cada integrante sigue funcionando con SQLite (`STORAGE_BACKEND=local`).

## Costos aproximados (us-east-1, N. Virginia)
| Recurso | Tamaño | Costo |
|---|---|---|
| EC2 (app + MongoDB) | t3.medium: 2 vCPU, 4 GB (el modelo de búsqueda necesita > 2 GB) | ~0,04 USD/hora |
| Disco del EC2 | 30 GB gp3 | ~0,08 USD/día |
| IP pública | 1 | ~0,005 USD/hora |
| S3 | unos MB | centavos |

Prendido un día completo: ~1,2 USD. **Olvidado un mes: ~35 USD.** Por eso: alerta de gasto + borrar al final.

## 0. Antes de crear nada: alerta de gasto y región
- Billing and Cost Management → **Budgets** → Create budget → **Monthly cost budget** → **5 USD** → tu correo.
- Región (arriba a la derecha): **US East (N. Virginia) us-east-1**. Todo se crea ahí.

## 1. Bucket S3 (informes y resultados)
S3 → Create bucket → nombre único, ej. `junta-medica-informes-<iniciales>-2026` → **Block all public access**
activado → Create. Anotar el nombre (va en `S3_BUCKET`).

## 2. Rol IAM del servidor (para usar S3 sin claves)
IAM → Roles → Create role → **AWS service → EC2** → Next → (sin políticas) → nombre `junta-medica-ec2` → Create.
Abrir el rol → Add permissions → **Create inline policy** → JSON (poner tu bucket):
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:PutObject", "s3:GetObject"],
    "Resource": "arn:aws:s3:::junta-medica-informes-xxxx-2026/*"
  }]
}
```
Nombre `junta-medica-s3` → Create policy.

## 3. Servidor EC2
EC2 → Launch instance:
- Nombre `junta-medica` · imagen **Ubuntu Server 24.04 LTS** · tipo **t3.medium**.
- Key pair: **Proceed without a key pair** (se entra con *EC2 Instance Connect* desde el navegador).
- Network settings → Edit → security group nuevo `junta-medica-web`:
  - SSH, puerto 22, origen Anywhere (para EC2 Instance Connect).
  - Custom TCP, puerto **8501**, origen Anywhere (la app; tiene inicio de sesión).
  - **No** abrir el 27017: MongoDB queda solo dentro del servidor.
- Storage: **30 GB gp3**.
- Advanced details → IAM instance profile: **junta-medica-ec2**.
- Launch instance. Anotar la **Public IPv4 address**.

## 4. Instalar MongoDB en el servidor
EC2 → `junta-medica` → **Connect** → EC2 Instance Connect → Connect. En la terminal que se abre:
```bash
sudo apt-get update && sudo apt-get install -y gnupg curl python3.12-venv git
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
sudo apt-get update && sudo apt-get install -y mongodb-org
sudo systemctl enable --now mongod
```
Crear el usuario de la aplicación (cambiar `CLAVE_MONGO` por una clave propia, sin `@ : / #`) y activar contraseña:
```bash
mongosh --quiet --eval 'db.getSiblingDB("junta_medica").createUser({user: "junta_app", pwd: "CLAVE_MONGO", roles: [{role: "readWrite", db: "junta_medica"}, {role: "readWrite", db: "junta_medica_test"}]})'
echo -e "security:\n  authorization: enabled" | sudo tee -a /etc/mongod.conf
sudo systemctl restart mongod
```

## 5. Instalar la app
```bash
git clone https://github.com/CarlosRaul04/junta-medica.git junta-medica-ia
# repositorio privado: usuario de GitHub y, como contraseña, un token (github.com/settings/tokens, permiso "repo")
cd junta-medica-ia
python3.12 -m venv .venv && source .venv/bin/activate
pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu   # PyTorch sin GPU (más liviano)
pip install -r requirements.txt
cp .env.ejemplo .env && nano .env
```
En el `.env` (guardar con Ctrl+O, Enter, Ctrl+X):
```
MOCK_MODE=0
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...                    # tu clave de OpenRouter
AGENT_MODEL=nvidia/nemotron-3.5-super-vl:free
CHIEF_MODEL=nvidia/nemotron-3.5-super-vl:free
STORAGE_BACKEND=aws
MONGODB_URI=mongodb://junta_app:CLAVE_MONGO@localhost:27017/junta_medica?authSource=junta_medica
MONGODB_DATABASE=junta_medica
S3_BUCKET=junta-medica-informes-xxxx-2026
AWS_REGION=us-east-1
```
Probar y arrancar:
```bash
STORAGE_BACKEND=local TEST_MONGODB_URI="mongodb://junta_app:CLAVE_MONGO@localhost:27017/junta_medica_test?authSource=junta_medica" python -m pytest -q
python -m scripts.index_guidelines     # base de búsqueda (descarga el modelo e5, ~5 min)
nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true > app.log 2>&1 &
```
> Con `TEST_MONGODB_URI` las pruebas de usuarios e historial corren también contra el MongoDB real del servidor
> (en la base aparte `junta_medica_test`).

Abrir **http://IP_PUBLICA:8501**. La primera cuenta que se cree será la de administrador.
Errores: `tail -f app.log` · detener: `pkill -f streamlit`.

## 6. Mostrar los datos en MongoDB (para la presentación)
```bash
mongosh "mongodb://junta_app:CLAVE_MONGO@localhost:27017/junta_medica?authSource=junta_medica"
show collections
db.users.find({}, {password_hash: 0})                     // cuentas (sin la contraseña)
db.consultations.find().sort({consultation_id: -1}).limit(3)   // últimas consultas
db.consultations.countDocuments({severe_alerts: {$gt: 0}})     // consultas con alertas graves
```
Los PDF: S3 → bucket → carpeta `reports/`.

## 7. Entre la prueba y la presentación
Probado el 2026-11-24: 396 pruebas (incluido MongoDB real), S3 con el rol IAM, búsqueda con 139 fragmentos y el
CASO-008 completo desde el navegador (usuario y consulta en MongoDB, PDF y JSON en S3).

Para actualizar el código en el servidor: `cd junta-medica-ia && git pull` (pide usuario y token) y volver a arrancar
la app (`pkill -f streamlit` y el comando `nohup streamlit ...`).

- **Apagar:** EC2 → Instance state → **Stop**. Apagado solo cobra el disco (~0,08 USD/día); MongoDB y los datos
  se conservan. Al prenderlo (**Start**) **cambia la IP pública**: entrar por Instance Connect y arrancar la app:
  ```bash
  cd junta-medica-ia && source .venv/bin/activate
  nohup streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true > app.log 2>&1 &
  ```
- O **borrar todo** (paso 8) y volver a crearlo el día de la presentación (~40 minutos).

## 8. Borrar todo (después de la presentación)
1. EC2 → instancia → Instance state → **Terminate** (borra el disco con MongoDB).
2. S3 → bucket → **Empty** → **Delete**.
3. IAM → Roles → `junta-medica-ec2` → Delete.
4. EC2 → Security Groups → borrar `junta-medica-web`.
5. Al día siguiente: Billing → **Bills**: confirmar que no siga sumando.

## Alternativa: Amazon DocumentDB (MongoDB administrado por AWS)
Si se pide que la base sea un servicio administrado (como RDS, pero para MongoDB), AWS ofrece **DocumentDB**,
compatible con MongoDB: el código funciona igual, solo cambia `MONGODB_URI`. Diferencias:
- Cuesta más: la instancia más chica (db.t3.medium) ronda 0,08 USD/hora, más almacenamiento y operaciones.
- Exige TLS: descargar el certificado (`wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem`) y usar
  `MONGODB_URI=mongodb://usuario:clave@ENDPOINT:27017/?tls=true&tlsCAFile=global-bundle.pem&retryWrites=false`.
- Se crea en la misma VPC que el EC2 y su security group solo debe aceptar el puerto 27017 desde el EC2.
- Al terminar: DocumentDB → borrar el clúster y su instancia (sin snapshot final).
