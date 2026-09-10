import React, { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";

const DARK_TILES = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const DARK_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

const COR_STATUS = {
  aberta:       "#ef4444",
  em_andamento: "#f59e0b",
  concluida:    "#22c55e",
};

function FlyTo({ foco }) {
  const map = useMap();
  useEffect(() => {
    if (foco?.latitude && foco?.longitude) {
      map.flyTo([foco.latitude, foco.longitude], 16, { duration: 0.8 });
    }
  }, [foco, map]);
  return null;
}

export default function Mapa({ demandas, foco }) {
  const comCoordenadas = demandas.filter((d) => d.latitude && d.longitude);

  const centro =
    comCoordenadas.length > 0
      ? [comCoordenadas[0].latitude, comCoordenadas[0].longitude]
      : [-23.7172, -46.8494];

  return (
    <div className="mapa-container">
      <MapContainer center={centro} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer url={DARK_TILES} attribution={DARK_ATTRIBUTION} />

        <FlyTo foco={foco} />

        {comCoordenadas.map((d) => {
          const cor = COR_STATUS[d.status] ?? "#94a3b8";
          const isFoco = foco?.id === d.id;
          return (
            <CircleMarker
              key={d.id}
              center={[d.latitude, d.longitude]}
              radius={isFoco ? 13 : 8}
              pathOptions={{
                color: isFoco ? "#f97316" : cor,
                fillColor: cor,
                fillOpacity: 0.9,
                weight: isFoco ? 3 : 1.5,
              }}
            >
              <Popup>
                <strong>#{d.protocolo}</strong>
                <br />
                {d.resumo || d.descricao?.slice(0, 80)}
                <br />
                <span style={{ color: cor, fontWeight: 600 }}>{d.status.replace("_", " ")}</span>
                {d.categoria && <> · {d.categoria}</>}
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
