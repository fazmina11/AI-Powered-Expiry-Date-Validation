"use client"

import { useEffect, useRef } from "react"
import { TestimonialsColumn } from "@/components/ui/testimonials-column"

export function TestimonialsSection() {
  const sectionRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const elements = entry.target.querySelectorAll(".fade-in-element")
            elements.forEach((element, index) => {
              setTimeout(() => {
                element.classList.add("animate-fade-in-up")
              }, index * 300)
            })
          }
        })
      },
      { threshold: 0.1 },
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => observer.disconnect()
  }, [])

  const testimonials = [
    {
      text: "Expired products that used to slip past our manual checks now get flagged instantly. We've prevented over ₹5 lakh in waste in just 3 months.",
      name: "Rajesh Kumar",
      role: "Warehouse Manager",
    },
    {
      text: "The accuracy is incredible. We went from 8% miss rate on expiry dates to 0.2%. Our customers now trust that every product is fresh.",
      name: "Priya Sharma",
      role: "Quality Control Manager",
    },
    {
      text: "Processing time for intake went from 15 minutes per pallet to 3 minutes. Our team can now focus on other critical tasks.",
      name: "Vikram Patel",
      role: "Logistics Director",
    },
    {
      text: "The compliance documentation this system generates automatically has saved us countless hours during audits. Regulators are impressed.",
      name: "Ananya Gupta",
      role: "Compliance Officer",
    },
    {
      text: "We love the classification system. Products marked for priority sale reduce our losses significantly, and Accept items move straight to inventory.",
      name: "Suresh Reddy",
      role: "Inventory Controller",
    },
    {
      text: "Integration with our ERP was seamless. Rejected items are automatically flagged, and shelf-life data flows perfectly into our tracking system.",
      name: "Meera Desai",
      role: "Operations Head",
    },
    {
      text: "The real-time alerts have been a game-changer. We catch near-expiry items before they hit the shelves, preventing customer returns.",
      name: "Arjun Singh",
      role: "Warehouse Supervisor",
    },
    {
      text: "ROI was clear within 6 weeks. The waste reduction alone pays for the system, and accuracy improvements are simply exceptional.",
      name: "Deepti Verma",
      role: "CFO, Food Distribution",
    },
  ]

  return (
    <section id="testimonials" ref={sectionRef} className="relative pt-16 pb-16 px-4 sm:px-6 lg:px-8">
      {/* Grid Background */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="h-full w-full"
          style={{
            backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
            backgroundSize: "80px 80px",
          }}
        />
      </div>

      <div className="relative max-w-7xl mx-auto">
        {/* Header Section - Keep as user loves it */}
        <div className="text-center mb-16 md:mb-32">
          <div className="fade-in-element opacity-0 translate-y-8 transition-all duration-1000 ease-out inline-flex items-center gap-2 text-white/60 text-sm font-medium tracking-wider uppercase mb-6">
            <div className="w-8 h-px bg-white/30"></div>
            Warehouse Success Stories
            <div className="w-8 h-px bg-white/30"></div>
          </div>
          <h2 className="fade-in-element opacity-0 translate-y-8 transition-all duration-1000 ease-out text-5xl md:text-6xl lg:text-7xl font-light text-white mb-8 tracking-tight text-balance">
            Warehouses that <span className="font-medium italic">eliminated waste</span>
          </h2>
          <p className="fade-in-element opacity-0 translate-y-8 transition-all duration-1000 ease-out text-xl text-white/70 max-w-2xl mx-auto leading-relaxed">
            See how food and beverage warehouses are preventing expired products and saving millions with intelligent validation
          </p>
        </div>

        {/* Testimonials Carousel */}
        <div className="fade-in-element opacity-0 translate-y-8 transition-all duration-1000 ease-out relative flex justify-center items-center min-h-[600px] md:min-h-[800px] overflow-hidden">
          <div
            className="flex gap-8 max-w-6xl"
            style={{
              maskImage: "linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%)",
              WebkitMaskImage: "linear-gradient(to bottom, transparent 0%, black 10%, black 90%, transparent 100%)",
            }}
          >
            <TestimonialsColumn testimonials={testimonials.slice(0, 3)} duration={15} className="flex-1" />
            <TestimonialsColumn
              testimonials={testimonials.slice(2, 5)}
              duration={12}
              className="flex-1 hidden md:block"
            />
            <TestimonialsColumn
              testimonials={testimonials.slice(1, 4)}
              duration={18}
              className="flex-1 hidden lg:block"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
