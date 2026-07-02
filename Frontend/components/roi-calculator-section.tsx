"use client"

import { useState, useEffect } from "react"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card } from "@/components/ui/card"
import { TrendingUp, Users, DollarSign, Clock } from "lucide-react"

interface CalculatorInputs {
  dailyProductsReceived: number
  currentErrorRate: number
  avgProductValue: number
  wastePercentage: number
}

export function ROICalculatorSection() {
  const [inputs, setInputs] = useState<CalculatorInputs>({
    dailyProductsReceived: 500,
    currentErrorRate: 8,
    avgProductValue: 200,
    wastePercentage: 3,
  })

  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
          }
        })
      },
      { threshold: 0.1 },
    )

    const section = document.getElementById("roi-calculator")
    if (section) {
      observer.observe(section)
    }

    return () => observer.disconnect()
  }, [])

  const getBusinessDefaults = () => {
    const businessDefaults = {
      food_retail: { avgValue: 150, maxValue: 500, accuracy: 99.8, timePerProduct: 0.5, errorReduction: 95 },
      beverage: { avgValue: 200, maxValue: 800, accuracy: 99.8, timePerProduct: 0.4, errorReduction: 96 },
      pharma: { avgValue: 400, maxValue: 2000, accuracy: 99.95, timePerProduct: 0.6, errorReduction: 98 },
      logistics: { avgValue: 180, maxValue: 600, accuracy: 99.8, timePerProduct: 0.45, errorReduction: 94 },
      default: { avgValue: 200, maxValue: 1000, accuracy: 99.8, timePerProduct: 0.5, errorReduction: 95 },
    }

    return businessDefaults[inputs.businessType as keyof typeof businessDefaults] || businessDefaults.default
  }

  const businessConfig = getBusinessDefaults()
  const improvements = {
    accuracy: businessConfig.accuracy,
    timePerProduct: businessConfig.timePerProduct,
    errorReduction: businessConfig.errorReduction,
  }

  // Current metrics (monthly)
  const monthlyProductsReceived = inputs.dailyProductsReceived * 25
  const currentWastedProducts = Math.round((monthlyProductsReceived * inputs.currentErrorRate) / 100)
  const currentWasteCost = currentWastedProducts * inputs.avgProductValue * (inputs.wastePercentage / 100)
  const currentProcessingTime = monthlyProductsReceived * 0.2 // 12 seconds per product manually

  // Improved metrics with AI system
  const improvedErrorRate = inputs.currentErrorRate * ((100 - improvements.errorReduction) / 100)
  const improvedWastedProducts = Math.round((monthlyProductsReceived * improvedErrorRate) / 100)
  const improvedWasteCost = improvedWastedProducts * inputs.avgProductValue * (inputs.wastePercentage / 100)
  const improvedProcessingTime = monthlyProductsReceived * improvements.timePerProduct

  // Gains
  const preventedWaste = currentWastedProducts - improvedWastedProducts
  const monthlySavings = currentWasteCost - improvedWasteCost
  const timeSaved = currentProcessingTime - improvedProcessingTime
  const savingsPercentage = ((currentWasteCost - improvedWasteCost) / currentWasteCost) * 100

  return (
    <section id="roi-calculator" className="py-16 md:py-20 px-4 relative">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div
          className={`text-center mb-12 md:mb-16 transition-all duration-700 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-6">
            <TrendingUp className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-white/80">ROI Calculator</span>
          </div>

          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-4 md:mb-6 text-balance">
            Calculate your{" "}
            <span className="bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              waste prevention savings
            </span>
          </h2>

          <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto text-balance">
            See how much money and product waste your warehouse could prevent every month with automated expiry validation
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 lg:gap-10 items-stretch">
          {/* Calculator Inputs */}
          <div
            className={`transition-all duration-700 delay-200 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <Card className="p-6 md:p-8 bg-[radial-gradient(35%_128px_at_50%_0%,theme(backgroundColor.white/15%),theme(backgroundColor.white/5%))] border-white/20 backdrop-blur-sm shadow-2xl h-full flex flex-col">
              <h3 className="text-xl md:text-2xl font-semibold text-white mb-6 md:mb-8">Your Business Metrics</h3>

              <div className="space-y-8 flex-1">
                {/* Warehouse Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">Warehouse Type</label>
                  <Select
                    value={inputs.businessType}
                    onValueChange={(value) => setInputs((prev) => ({ ...prev, businessType: value }))}
                  >
                    <SelectTrigger className="bg-gray-700/50 border-gray-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-800 border-gray-700">
                      <SelectItem value="food_retail">Food Retail</SelectItem>
                      <SelectItem value="beverage">Beverage Distribution</SelectItem>
                      <SelectItem value="pharma">Pharmaceutical</SelectItem>
                      <SelectItem value="logistics">Logistics Hub</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Daily Products */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Daily Products Received:{" "}
                    <span className="text-white font-semibold">{inputs.dailyProductsReceived.toLocaleString()}</span>
                  </label>
                  <Slider
                    value={[inputs.dailyProductsReceived]}
                    onValueChange={([value]) => setInputs((prev) => ({ ...prev, dailyProductsReceived: value }))}
                    max={5000}
                    min={100}
                    step={100}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>100</span>
                    <span>5K</span>
                  </div>
                </div>

                {/* Current Error Rate */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Current Expiry Miss Rate:{" "}
                    <span className="text-white font-semibold">{inputs.currentErrorRate}%</span>
                  </label>
                  <Slider
                    value={[inputs.currentErrorRate]}
                    onValueChange={([value]) => setInputs((prev) => ({ ...prev, currentErrorRate: value }))}
                    max={20}
                    min={1}
                    step={0.5}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>1%</span>
                    <span>20%</span>
                  </div>
                </div>

                {/* Average Product Value */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Average Product Value:{" "}
                    <span className="text-white font-semibold">₹{inputs.avgProductValue.toLocaleString()}</span>
                  </label>
                  <Slider
                    value={[inputs.avgProductValue]}
                    onValueChange={([value]) => setInputs((prev) => ({ ...prev, avgProductValue: value }))}
                    max={1000}
                    min={50}
                    step={50}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>₹50</span>
                    <span>₹{businessConfig.maxValue?.toLocaleString() || "1000"}</span>
                  </div>
                </div>

                <div className="flex-1"></div>
              </div>

              <div className="mt-6 lg:hidden">
                <div className="flex items-center justify-center gap-2 p-3 rounded-lg bg-primary/10 border border-primary/20">
                  <div className="animate-bounce">
                    <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 14l-7 7m0 0l-7-7m7 7V3"
                      />
                    </svg>
                  </div>
                  <span className="text-sm text-primary font-medium">Scroll down to see your results</span>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-700/50">
                <div className="space-y-4">
                  <h4 className="text-sm font-semibold text-gray-300 mb-3">📊 System Performance</h4>
                  <div className="space-y-3">
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                      <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                      <div>
                        <p className="text-sm text-gray-300">
                          <span className="font-medium text-white">Detection accuracy:</span> {businessConfig.accuracy}% with advanced AI
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                      <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                      <div>
                        <p className="text-sm text-gray-300">
                          <span className="font-medium text-white">Processing speed:</span> {businessConfig.timePerProduct} seconds per product
                        </p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                      <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                      <div>
                        <p className="text-sm text-gray-300">
                          <span className="font-medium text-white">Error reduction:</span> Up to {businessConfig.errorReduction}% fewer missed expirations
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Results */}
          <div
            className={`transition-all duration-700 delay-400 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <Card className="p-6 md:p-8 bg-[radial-gradient(35%_128px_at_50%_0%,theme(backgroundColor.white/15%),theme(backgroundColor.white/5%))] border-white/20 backdrop-blur-sm shadow-2xl h-full flex flex-col">
              <h3 className="text-xl md:text-2xl font-semibold text-white mb-6 md:mb-8">
                Monthly Savings with Our System
              </h3>

              <div className="space-y-6 flex-1">
                {/* Current vs Prevented Waste */}
                <div className="grid grid-cols-2 gap-3 md:gap-4">
                  <div className="text-center p-3 md:p-4 rounded-lg bg-gray-700/30">
                    <div className="text-xs md:text-sm text-gray-400 mb-1">Currently Lost</div>
                    <div className="text-xl md:text-2xl font-bold text-red-400">{currentWastedProducts}</div>
                    <div className="text-xs text-gray-400">products wasted</div>
                  </div>
                  <div className="text-center p-3 md:p-4 rounded-lg bg-white/10 border border-white/20">
                    <div className="text-xs md:text-sm text-gray-300 mb-1">With System</div>
                    <div className="text-xl md:text-2xl font-bold text-green-400">{improvedWastedProducts}</div>
                    <div className="text-xs text-gray-300">products wasted</div>
                  </div>
                </div>

                <div className="space-y-3 md:space-y-4">
                  <div className="flex items-center justify-between p-3 md:p-4 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-3">
                      <Users className="w-4 h-4 md:w-5 md:h-5 text-gray-300" />
                      <span className="text-sm md:text-base text-white">Products Prevented</span>
                    </div>
                    <span className="text-lg md:text-xl font-bold text-green-400">+{preventedWaste}</span>
                  </div>

                  <div className="flex items-center justify-between p-3 md:p-4 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-3">
                      <DollarSign className="w-4 h-4 md:w-5 md:h-5 text-gray-300" />
                      <span className="text-sm md:text-base text-white">Monthly Waste Savings</span>
                    </div>
                    <span className="text-lg md:text-xl font-bold text-green-400">
                      ₹{monthlySavings.toLocaleString("en-IN", {maximumFractionDigits: 0})}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-3 md:p-4 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-3">
                      <TrendingUp className="w-4 h-4 md:w-5 md:h-5 text-gray-300" />
                      <span className="text-sm md:text-base text-white">Waste Reduction</span>
                    </div>
                    <span className="text-lg md:text-xl font-bold text-green-400">{savingsPercentage.toFixed(1)}%</span>
                  </div>

                  <div className="flex items-center justify-between p-3 md:p-4 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-3">
                      <Clock className="w-4 h-4 md:w-5 md:h-5 text-gray-300" />
                      <span className="text-sm md:text-base text-white">Time Saved Monthly</span>
                    </div>
                    <span className="text-lg md:text-xl font-bold text-white">{(timeSaved / 60).toFixed(0)} hours</span>
                  </div>
                </div>

                {/* Annual Projection */}
                <div className="mt-6 md:mt-8 p-4 md:p-6 rounded-lg bg-white/5 border border-white/10">
                  <div className="text-center">
                    <div className="text-xs md:text-sm text-gray-300 mb-2">Projected Annual Savings</div>
                    <div className="text-2xl md:text-3xl lg:text-4xl font-bold text-green-400 mb-2">
                      ₹{(monthlySavings * 12).toLocaleString("en-IN", {maximumFractionDigits: 0})}
                    </div>
                    <div className="text-xs md:text-sm text-gray-400">
                      Based on your warehouse metrics and system efficiency
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>

        {/* CTA */}
        <div
          className={`text-center mt-12 md:mt-16 transition-all duration-700 delay-600 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
        >
          <p className="text-sm text-gray-400 mt-4">* Results based on industry averages and may vary by business</p>
        </div>
      </div>
    </section>
  )
}
