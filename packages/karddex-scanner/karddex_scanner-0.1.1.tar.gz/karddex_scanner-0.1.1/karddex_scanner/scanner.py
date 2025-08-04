import os
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

import openai

# Carrega a chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

@dataclass
class Attack:
    name: str
    cost: List[str] = field(default_factory=list)
    damage: Optional[str] = None
    text: Optional[str] = None

@dataclass
class CardData:
    name: str
    set: str
    number: str
    rarity: Optional[str] = None
    illustrator: Optional[str] = None
    hp: Optional[int] = None
    type: Optional[str] = None
    attacks: List[Attack] = field(default_factory=list)
    weaknesses: List[Dict[str, str]] = field(default_factory=list)
    resistances: List[Dict[str, str]] = field(default_factory=list)
    retreat_cost: List[str] = field(default_factory=list)
    text: Optional[str] = None

def extract_card_data(ocr_json: Dict[str, Any]) -> CardData:
    """
    Recebe JSON de OCR bruto e retorna um CardData com todos os campos extraídos.
    """
    ocr_text = json.dumps(ocr_json, ensure_ascii=False, indent=2)

    system_prompt = (
        "Você é um parser especializado em cartas Pokémon. "
        "Receberá um JSON de OCR e deve retornar SOMENTE um JSON "
        "válido seguindo o schema CardData, sem explicações adicionais."
    )
    user_prompt = f"Aqui está o JSON de OCR:\n```json\n{ocr_text}\n```"

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        functions=[
            {
                "name": "extract_card_data",
                "description": "Extrai dados de carta Pokémon",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "set": {"type": "string"},
                        "number": {"type": "string"},
                        "rarity": {"type": "string"},
                        "illustrator": {"type": "string"},
                        "hp": {"type": "integer"},
                        "type": {"type": "string"},
                        "attacks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "cost": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "damage": {"type": "string"},
                                    "text": {"type": "string"}
                                },
                                "required": ["name"]
                            }
                        },
                        "weaknesses": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "value": {"type": "string"}
                                }
                            }
                        },
                        "resistances": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string"},
                                    "value": {"type": "string"}
                                }
                            }
                        },
                        "retreat_cost": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "text": {"type": "string"}
                    },
                    "required": ["name", "set", "number", "attacks"]
                }
            }
        ],
        function_call={"name": "extract_card_data"}
    )

    fc = resp.choices[0].message.function_call
    args = json.loads(fc.arguments)

    attacks = [
        Attack(
            name=a["name"],
            cost=a.get("cost", []),
            damage=a.get("damage"),
            text=a.get("text")
        ) for a in args.get("attacks", [])
    ]

    return CardData(
        name=args["name"],
        set=args["set"],
        number=args["number"],
        rarity=args.get("rarity"),
        illustrator=args.get("illustrator"),
        hp=args.get("hp"),
        type=args.get("type"),
        attacks=attacks,
        weaknesses=args.get("weaknesses", []),
        resistances=args.get("resistances", []),
        retreat_cost=args.get("retreat_cost", []),
        text=args.get("text")
    )
