"use client"

import { useEffect, useRef } from "react"

interface GraphNode {
  id:        string
  is_mule?:  boolean
  score?:    number
}

interface GraphLink {
  source: string
  target: string
  amount: number
}

interface GraphProps {
  nodes: GraphNode[]
  links: GraphLink[]
  width?: number
  height?: number
}

export default function ForceGraph({ nodes, links, width = 600, height = 400 }: GraphProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return

    // Lazy-load D3 to avoid SSR issues
    import("d3").then((d3) => {
      const svg = d3.select(svgRef.current)
      svg.selectAll("*").remove()

      const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
        .force("link",   d3.forceLink(links).id((d: any) => d.id).distance(80))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collision", d3.forceCollide(20))

      // Arrow marker
      svg.append("defs").append("marker")
        .attr("id", "arrowhead")
        .attr("viewBox", "-0 -5 10 10")
        .attr("refX", 18).attr("refY", 0)
        .attr("orient", "auto").attr("markerWidth", 8).attr("markerHeight", 8)
        .append("path")
        .attr("d", "M 0,-5 L 10,0 L 0,5")
        .attr("fill", "#8b1a1a")

      const link = svg.append("g")
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke", "#8b1a1a")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", (d) => Math.log1p(d.amount / 10000))
        .attr("marker-end", "url(#arrowhead)")

      const node = svg.append("g")
        .selectAll("circle")
        .data(nodes)
        .join("circle")
        .attr("r", 10)
        .attr("fill", (d) => d.is_mule ? "#8b1a1a" : d.score && d.score > 0.7 ? "#c17a00" : "#1a4a3c")
        .attr("stroke", "#f4f1e8")
        .attr("stroke-width", 1.5)
        .call(
          d3.drag<SVGCircleElement, GraphNode>()
            .on("start", (event, d: any) => {
              if (!event.active) simulation.alphaTarget(0.3).restart()
              d.fx = d.x; d.fy = d.y
            })
            .on("drag", (event, d: any) => { d.fx = event.x; d.fy = event.y })
            .on("end", (event, d: any) => {
              if (!event.active) simulation.alphaTarget(0)
              d.fx = null; d.fy = null
            }) as any
        )

      const label = svg.append("g")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("font-size", "9px")
        .attr("fill", "#f4f1e8")
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .text((d) => d.id.slice(-6))

      simulation.on("tick", () => {
        link
          .attr("x1", (d: any) => d.source.x)
          .attr("y1", (d: any) => d.source.y)
          .attr("x2", (d: any) => d.target.x)
          .attr("y2", (d: any) => d.target.y)
        node
          .attr("cx", (d: any) => d.x)
          .attr("cy", (d: any) => d.y)
        label
          .attr("x", (d: any) => d.x)
          .attr("y", (d: any) => d.y)
      })
    })
  }, [nodes, links, width, height])

  return (
    <div className="relative bg-white/5 rounded-lg overflow-hidden border border-white/10">
      <div className="absolute top-2 left-3 text-[10px] text-gray-400 z-10">
        <span className="inline-block w-2 h-2 rounded-full bg-red-700 mr-1" />Mule
        <span className="inline-block w-2 h-2 rounded-full bg-yellow-600 mx-1 ml-3" />High Risk
        <span className="inline-block w-2 h-2 rounded-full bg-teal-700 mx-1 ml-3" />Legitimate
      </div>
      <svg ref={svgRef} width={width} height={height} />
    </div>
  )
}
