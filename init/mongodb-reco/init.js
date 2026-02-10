// Base: reco
// Moteur de recommandation - stockage des recommandations (plans, programmes, etc.)

db = db.getSiblingDB("reco");

// Collection recommendations - recommandations générées par le moteur
// Schéma flexible selon type (nutrition, activité, etc.)
if (!db.getCollectionNames().includes("recommendations")) {
  db.createCollection("recommendations");
  db.recommendations.createIndex({ id_anonyme: 1 });
  db.recommendations.createIndex({ type: 1 });
  db.recommendations.createIndex({ created_at: 1 });
}

// ---- JEU DE DONNÉES (si collection vide) ----
const UUID_MARIE = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11";
const UUID_LUCAS = "b1ffcd00-ad1c-4ef9-cc7e-7cc0ce491b22";
const UUID_LEA = "c2aadf11-be2d-4ef0-dd8f-8dd1df5a2c33";

if (db.recommendations.countDocuments() === 0) {
  db.recommendations.insertMany([
    { id_anonyme: UUID_MARIE, type: "nutrition", titre: "Équilibrez votre petit-déjeuner", contenu: "Augmentez les protéines le matin (oeufs, fromage blanc) pour tenir jusqu'au déjeuner.", created_at: new Date("2025-02-07T10:00:00Z"), score: 0.85 },
    { id_anonyme: UUID_MARIE, type: "activite", titre: "Séance full body", contenu: "Squats, pompes, gainage - 3x12 répétitions, RPE 6.", created_at: new Date("2025-02-06T18:00:00Z"), score: 0.9 },
    { id_anonyme: UUID_LUCAS, type: "nutrition", titre: "Objectif prise de masse", contenu: "Viser 2500 kcal/jour avec 1.8 g protéines/kg. Collation 16h recommandée.", created_at: new Date("2025-02-05T12:00:00Z"), score: 0.88 },
    { id_anonyme: UUID_LUCAS, type: "activite", titre: "Programme force", contenu: "Séances dos/jambes et haut du corps en alternance, 4 séries 6-8 reps.", created_at: new Date("2025-02-04T09:00:00Z"), score: 0.92 },
    { id_anonyme: UUID_LEA, type: "nutrition", titre: "Plans végétariens", contenu: "Lentilles, pois chiches et tofu pour couvrir les protéines sans viande.", created_at: new Date("2025-02-08T14:00:00Z"), score: 0.87 },
    { id_anonyme: UUID_LEA, type: "activite", titre: "HIIT maison", contenu: "30s effort / 30s récup, burpees, mountain climbers, jumping jacks - 20 min.", created_at: new Date("2025-02-07T11:00:00Z"), score: 0.91 }
  ]);
}
