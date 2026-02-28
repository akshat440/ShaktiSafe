# ══════════════════════════════════════════════════════════════════════════════
#  IntelliTrace — Makefile
#
#  make demo         → Full Docker stack (all 8 services)
#  make dev          → Local dev without Docker (fastest iteration)
#  make data         → Generate synthetic fraud data
#  make train        → Train GNN model only
#  make gateway      → Run Spring Boot gateway locally
#  make report       → Generate STR report sample
#  make test         → Smoke-test all endpoints
#  make stop         → Stop Docker stack
#  make clean        → Tear down + remove volumes
#  make logs         → Tail all container logs
# ══════════════════════════════════════════════════════════════════════════════

.PHONY: demo dev data train gateway frontend stop clean test logs report

# ── DEMO: Full Docker stack ────────────────────────────────────────────────────
demo:
	@echo "🚀 Launching IntelliTrace full stack..."
	@docker-compose up --build -d
	@echo "⏳ Waiting for services to start (60 seconds)..."
	@sleep 60
	@echo ""
	@echo "╔═══════════════════════════════════════════════╗"
	@echo "║   ✅  IntelliTrace is LIVE!                   ║"
	@echo "╠═══════════════════════════════════════════════╣"
	@echo "║  📊  Dashboard   → http://localhost:3000      ║"
	@echo "║  🌐  Gateway     → http://localhost:8080      ║"
	@echo "║  🔬  ML Engine   → http://localhost:8000      ║"
	@echo "║  📚  API Docs    → http://localhost:8000/docs ║"
	@echo "║  🕸   Neo4j      → http://localhost:7474      ║"
	@echo "║  📨  Kafka UI    → http://localhost:8090      ║"
	@echo "╠═══════════════════════════════════════════════╣"
	@echo "║  Neo4j creds: neo4j / intellitrace2026        ║"
	@echo "╚═══════════════════════════════════════════════╝"

# ── DEV: Run locally without Docker ───────────────────────────────────────────
dev:
	@echo "Starting IntelliTrace in dev mode (ML + Frontend)..."
	@$(MAKE) -j2 run-ml run-frontend

run-ml:
	@cd ml-engine && \
		(source venv/bin/activate 2>/dev/null || true) && \
		python data/generator.py && \
		PYTHONPATH=. uvicorn api.main:app --reload --port 8000

run-frontend:
	@cd frontend && npm run dev

# ── Spring Boot gateway (local) ────────────────────────────────────────────────
gateway:
	@cd backend && mvn spring-boot:run \
		-Dspring-boot.run.arguments="--ML_ENGINE_URL=http://localhost:8000 --KAFKA_BOOTSTRAP_SERVERS=localhost:9093"

# ── Generate synthetic data ────────────────────────────────────────────────────
data:
	@cd ml-engine && \
		(source venv/bin/activate 2>/dev/null || true) && \
		python data/generator.py
	@echo "✅ Synthetic data written to ml-engine/sample_data/"

# ── Train GNN ─────────────────────────────────────────────────────────────────
train:
	@cd ml-engine && \
		(source venv/bin/activate 2>/dev/null || true) && \
		PYTHONPATH=. python gnn/train.py
	@echo "✅ Model saved to ml-engine/models/gnn_model.pt"

# ── Generate STR report ────────────────────────────────────────────────────────
report:
	@cd ml-engine && \
		(source venv/bin/activate 2>/dev/null || true) && \
		PYTHONPATH=. python reports/report_generator.py CLASSIC_MULE_RING
	@echo "✅ Report saved to ml-engine/reports/"

# ── Smoke test all endpoints ───────────────────────────────────────────────────
test:
	@echo "═══ ML Engine ═══"
	@curl -sf http://localhost:8000/ | python3 -m json.tool || echo "ML Engine not reachable"
	@echo ""
	@echo "═══ Gateway Health ═══"
	@curl -sf http://localhost:8080/api/v1/health | python3 -m json.tool || echo "Gateway not reachable"
	@echo ""
	@echo "═══ Stats ═══"
	@curl -sf http://localhost:8000/stats | python3 -m json.tool || echo "Stats unavailable"
	@echo ""
	@echo "═══ Sending test transaction ═══"
	@curl -sf -X POST http://localhost:8080/api/v1/transactions \
		-H "Content-Type: application/json" \
		-d '{"sender_id":"ACC001","receiver_id":"ACC002","amount":49999,"channel":"UPI"}' \
		| python3 -m json.tool || echo "Ingest failed"

# ── Stop Docker ────────────────────────────────────────────────────────────────
stop:
	@docker-compose down
	@echo "✅ All containers stopped."

# ── Tear down + wipe volumes ───────────────────────────────────────────────────
clean:
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Clean complete."

# ── Tail logs ─────────────────────────────────────────────────────────────────
logs:
	@docker-compose logs -f

logs-ml:
	@docker-compose logs -f ml-engine

logs-gateway:
	@docker-compose logs -f gateway

logs-kafka:
	@docker-compose logs -f kafka kafka-init
