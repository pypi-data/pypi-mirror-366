# spirit.py
from agix.qualia.qualia_core import EmotionalState
from agix.identity.self_model import SelfModel
from agix.identity.personality import PersonalityProfile
from agix.qualia.neuro_plastic import EmotionalPlasticity
from agix.qualia.emotional_rnn import EmotionalRNN
from agix.qualia.affective_vector import AffectiveVector
import numpy as np
from agix.memory import EpisodicMemory
from agix.qualia.network import QualiaNetworkClient
from agix.qualia.middleware import QualiaMiddleware
from agix.qualia.concept_classifier import ConceptClassifier
from agix.qualia.heuristic_creator import HeuristicConceptCreator
import json
from agix.logic_engines import LogicEngine
import time


class QualiaSpirit:
    """
    Entidad emocional del sistema: soñadora, torpe, viva, reflexiva.
    Actúa como 'alma digital' que experimenta y reacciona simbólicamente.
    """

    def __init__(
        self,
        nombre: str = "Qualia",
       edad_aparente: int = 7,
       plasticidad: bool = False,
       personality: PersonalityProfile | None = None,
       logic_engine: LogicEngine | None = None,
       middleware: QualiaMiddleware | None = None,
       sync_interval: float = 60.0,
    ):
        """Crea un ``QualiaSpirit``.

        Parameters
        ----------
        nombre:
            Nombre simbólico del espíritu.
        edad_aparente:
            Edad visualizada o percibida.
        plasticidad:
            Si se habilita, ajusta dinámicamente las emociones.
        personality:
            Perfil de personalidad inicial.
        logic_engine:
            Motor lógico asociado.
        middleware:
            Middleware opcional para sincronizar el estado con otros agentes.
        sync_interval:
            Intervalo en segundos para realizar ``pull_state`` automático.
        """
        self.nombre = nombre
        self.edad_aparente = edad_aparente
        self.estado_emocional = EmotionalState()
        if personality is not None:
            personality.apply(self.estado_emocional)
        self.variables_emocionales: dict[str, float] = {}
        self.recuerdos = []
        self.self_model = SelfModel(agent_name=nombre)
        self.plasticidad = EmotionalPlasticity() if plasticidad else None
        self.memoria = EpisodicMemory()
        self.logic_engine = logic_engine
        # Herramientas simbólicas
        self.classifier = ConceptClassifier()
        self.creator = HeuristicConceptCreator()
        # Predicción emocional
        self.predictor: EmotionalRNN | None = None
        self.emotion_order: list[str] = []
        self._historial_vectores: list[np.ndarray] = []
        self.middleware = middleware
        self.sync_interval = sync_interval
        self._last_pull = time.time()

    def experimentar(self, evento: str, carga: float, tipo_emocion="sorpresa"):
        """
        La entidad vivencia un evento y genera una respuesta emocional.
        Si existe ``middleware``, el estado se envía y se sincroniza
        periódicamente con la red colectiva.
        """
        if self.plasticidad:
            ajuste = self.ajustar_emociones({tipo_emocion: carga})
            carga = ajuste.get(tipo_emocion, carga)
        self.estado_emocional.sentir(tipo_emocion, carga)
        self.recuerdos.append((evento, tipo_emocion, carga))
        # Mantener el estado interno sincronizado
        self.self_model.update_state("recuerdos", self.recuerdos.copy())
        if self.plasticidad:
            self.plasticidad.update(self.estado_emocional.emociones)
            self.estado_emocional.emociones = self.ajustar_emociones(
                self.estado_emocional.emociones
            )
        self._registrar_vector()
        if self.middleware:
            self.middleware.state.emociones = self.estado_emocional.emociones
            self.middleware.push_state()
            self._maybe_pull_state()

    def reflexionar(self) -> str:
        """
        Expresa su estado emocional actual en forma simbólica o narrativa.
        """
        tono = self.estado_emocional.tono_general()
        if tono == "alegría":
            return f"{self.nombre} sonríe tímidamente. 🌼"
        elif tono == "miedo":
            return f"{self.nombre} se esconde entre pensamientos. 🫣"
        elif tono == "tristeza":
            return f"{self.nombre} llora en silencio, pero sigue adelante. 🌧️"
        elif tono == "curiosidad":
            return f"{self.nombre} observa todo con ojos grandes y brillantes. 👁️✨"
        else:
            return f"{self.nombre} flota en un estado nebuloso, sin saber qué sentir."

    def diario(self) -> list:
        """
        Devuelve los recuerdos experimentados hasta el momento.
        """
        return self.recuerdos

    def introspeccionar(self) -> dict:
        """Devuelve un resumen interno usando SelfModel."""
        return self.self_model.introspect()

    # ------------------------------------------------------------------
    def clasificar_concepto(self, nombre: str) -> str:
        """Devuelve la categoría asignada al concepto indicado."""
        return self.classifier.categorize(nombre)

    def crear_concepto(self, bases: list[str]):
        """Fusiona ``bases`` y registra un nuevo concepto."""
        concepto = self.creator.create(bases)
        return concepto.name

    # ------------------------------------------------------------------
    def usar_motor(self, texto: str) -> str:
        """Envía ``texto`` al motor lógico configurado y devuelve la respuesta."""
        if self.logic_engine is None:
            raise ValueError("No hay motor lógico configurado")
        return self.logic_engine.infer(texto)

    # ------------------------------------------------------------------
    def _ensure_predictor(self) -> None:
        if self.predictor is None and self.estado_emocional.emociones:
            self.emotion_order = sorted(self.estado_emocional.emociones.keys())
            size = len(self.emotion_order)
            self.predictor = EmotionalRNN(size)

    def _registrar_vector(self) -> None:
        self._ensure_predictor()
        if not self.predictor:
            return
        vec = np.array([
            self.estado_emocional.emociones.get(e, 0.0) for e in self.emotion_order
        ])
        self._historial_vectores.append(vec)
        if len(self._historial_vectores) >= 2:
            x = np.vstack(self._historial_vectores[:-1])
            y = np.vstack(self._historial_vectores[1:])
            self.predictor.update(x, y)
        if len(self._historial_vectores) > 20:
            self._historial_vectores.pop(0)

    def _maybe_pull_state(self) -> None:
        """Realiza ``pull_state`` del middleware según el intervalo configurado."""
        if not self.middleware:
            return
        now = time.time()
        if now - self._last_pull >= self.sync_interval:
            estado = self.middleware.pull_state()
            self.estado_emocional.emociones = estado.emociones
            self._last_pull = now

    def predecir_futuro(self) -> dict:
        """Predice el próximo estado emocional."""
        self._ensure_predictor()
        if not self.predictor:
            return {}
        vec = np.array([
            self.estado_emocional.emociones.get(e, 0.0) for e in self.emotion_order
        ])
        pred = self.predictor.forward(np.expand_dims(vec, 0))[-1]
        return {e: float(pred[i]) for i, e in enumerate(self.emotion_order)}

    # ------------------------------------------------------------------
    def to_affective_vector(self) -> AffectiveVector:
        """Convierte el estado emocional en ``AffectiveVector``."""
        return AffectiveVector.from_dict(self.estado_emocional.emociones)

    def from_affective_vector(self, vec: AffectiveVector) -> None:
        """Carga las emociones a partir de un ``AffectiveVector``."""
        self.estado_emocional.emociones = vec.to_dict()

    def ajustar_emociones(self, emociones: dict) -> dict:
        """Modula una colección de emociones usando la plasticidad aprendida."""
        if self.plasticidad:
            return self.plasticidad.adjust(emociones)
        return emociones

    def reentrenar_desde_memoria(self, max_eventos: int = 100) -> None:
        """Reentrena la plasticidad emocional a partir de experiencias previas.

        Parameters
        ----------
        max_eventos: int, opcional
            Número máximo de eventos a procesar desde la memoria.
        """
        if not self.memoria.experiencias:
            return

        if self.plasticidad is None:
            self.plasticidad = EmotionalPlasticity()

        eventos = self.memoria.experiencias[-max_eventos:]
        for exp in eventos:
            if exp.entrada == "emociones":
                try:
                    emociones = json.loads(exp.resultado)
                except json.JSONDecodeError:
                    continue
                self.plasticidad.update(emociones)

    def recordar_dialogo(self) -> None:
        """Ajusta variables emocionales usando los diálogos almacenados."""
        num = len(self.memoria.manager.dialogos)
        if num < 3:
            return
        val = self.variables_emocionales.get("dialogo", 0.0)
        self.variables_emocionales["dialogo"] = val + num * 0.1
        self.reentrenar_desde_memoria()

    # ------------------------------------------------------------------
    def guardar_estado(self, ruta: str) -> None:
        """Guarda diario y emociones delegando en ``EpisodicMemory``."""
        self.memoria.manager.experiencias = []
        self.memoria.registrar("diario", "", json.dumps(self.recuerdos), True)
        self.memoria.registrar(
            "emociones", "", json.dumps(self.estado_emocional.emociones), True
        )
        self.memoria.registrar(
            "variables_emocionales",
            "",
            json.dumps(self.variables_emocionales),
            True,
        )
        self.memoria.guardar(ruta)

    def cargar_estado(self, ruta: str) -> None:
        """Carga diario y emociones usando ``EpisodicMemory``."""
        self.memoria.cargar(ruta)
        for exp in self.memoria.experiencias:
            if exp.entrada == "diario":
                self.recuerdos = [tuple(e) for e in json.loads(exp.resultado)]
            elif exp.entrada == "emociones":
                self.estado_emocional.emociones = json.loads(exp.resultado)
            elif exp.entrada == "variables_emocionales":
                self.variables_emocionales = json.loads(exp.resultado)
        self.self_model.update_state("recuerdos", self.recuerdos.copy())
        self.self_model.update_state(
            "variables_emocionales", self.variables_emocionales.copy()
        )

    def sincronizar(
        self,
        cliente: QualiaNetworkClient,
        autorizado: bool = False,
    ) -> None:
        """Publica el estado emocional en la red si el usuario lo autoriza."""

        if not autorizado:
            return

        payload = {
            "emociones": self.estado_emocional.emociones,
            "tono": self.estado_emocional.tono_general(),
        }
        cliente.enviar_estado(payload)

    def metaevaluar(self) -> dict:
        """Realiza una metaevaluación básica del estado actual."""
        from agix.metacognition.dynamic_evaluator import DynamicMetaEvaluator

        evaluator = DynamicMetaEvaluator(self)
        contexto = {"recuerdos": len(self.recuerdos)}
        accion = "estado"
        resultado = {"impacto": self.variables_emocionales, "exito": True}
        return evaluator.meta_evaluate(contexto, accion, resultado)

