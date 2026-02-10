// Base: logs_config
// Collections: evenements (LOGS_EVENEMENTS), config (paramètres globaux)

db = db.getSiblingDB("logs_config");

// Collection evenements - correspond à LOGS_EVENEMENTS (BDD.txt)
// Champs: id_log, timestamp, id_anonyme (UUID), action, details_techniques (JSON)
if (!db.getCollectionNames().includes("evenements")) {
  db.createCollection("evenements");
  db.evenements.createIndex({ timestamp: 1 });
  db.evenements.createIndex({ id_anonyme: 1 });
  db.evenements.createIndex({ action: 1 });
}

// Collection config - paramètres globaux (clé / valeur ou document)
if (!db.getCollectionNames().includes("config")) {
  db.createCollection("config");
  db.config.createIndex({ cle: 1 }, { unique: true });
}

// ---- JEU DE DONNÉES (si collections vides) ----
const UUID_MARIE = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11";
const UUID_LUCAS = "b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22";
const UUID_LEA = "c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33";

if (db.evenements.countDocuments() === 0) {
  db.evenements.insertMany([
    { id_log: "log-001", timestamp: new Date("2025-02-08T18:45:00Z"), id_anonyme: UUID_MARIE, action: "connexion", details_techniques: { user_agent: "HealthAI/1.0", ip_hash: "xxx" } },
    { id_log: "log-002", timestamp: new Date("2025-02-08T18:46:00Z"), id_anonyme: UUID_MARIE, action: "consultation_journal", details_techniques: { page: "journal" } },
    { id_log: "log-003", timestamp: new Date("2025-02-07T20:00:00Z"), id_anonyme: UUID_LUCAS, action: "connexion", details_techniques: {} },
    { id_log: "log-004", timestamp: new Date("2025-02-07T20:05:00Z"), id_anonyme: UUID_LUCAS, action: "ajout_seance", details_techniques: { id_seance: 3 } },
    { id_log: "log-005", timestamp: new Date("2025-02-09T08:30:00Z"), id_anonyme: UUID_LEA, action: "connexion", details_techniques: {} },
    { id_log: "log-006", timestamp: new Date("2025-02-09T08:35:00Z"), id_anonyme: UUID_LEA, action: "consultation_recommandations", details_techniques: { type: "nutrition" } }
  ]);
}

if (db.config.countDocuments() === 0) {
  db.config.insertMany([
    { cle: "maintenance_mode", valeur: false, description: "Mode maintenance global" },
    { cle: "max_repas_journal", valeur: 10, description: "Nombre max de repas enregistrables par jour" },
    { cle: "feature_reco_ia", valeur: true, description: "Activation des recommandations IA" }
  ]);
}
