"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Package,
  AlertTriangle,
  Camera,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  X,
  Upload,
  Loader2,
  ShieldCheck,
  Info,
} from "lucide-react";
import { apiFetch } from "@/services/apiService";
import { cn } from "@/lib/utils";

// ─── Types ──────────────────────────────────────────────────────────────────

interface FormData {
  // Step 1 – Product Info
  product_name: string;
  barcode: string;
  batch_number: string;
  purchase_date: string;
  store_name: string;
  store_location: string;
  // Step 2 – Issue Info
  report_type: string;
  description: string;
  // Step 3 – Evidence (images as data-URLs for preview)
  images: File[];
  imagePreviews: string[];
}

interface FieldError {
  [key: string]: string;
}

interface SubmissionResult {
  id: string;
  created_at: string;
  status: string;
  barcode: string;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const ISSUE_TYPES = [
  { value: "LEAKAGE", label: "Leakage / Spillage", emoji: "💧" },
  { value: "WRONG_PRODUCT", label: "Wrong Product", emoji: "🔄" },
  { value: "DAMAGED_PACKAGING", label: "Damaged Packaging", emoji: "📦" },
  { value: "FOREIGN_OBJECT", label: "Foreign Object Found", emoji: "⚠️" },
  { value: "EXPIRED_PRODUCT", label: "Expired Product", emoji: "📅" },
  { value: "BAD_SMELL", label: "Bad Smell / Odour", emoji: "👃" },
  { value: "CONTAMINATION", label: "Contamination", emoji: "☣️" },
  { value: "OTHER", label: "Other Issue", emoji: "❓" },
];

const STEPS = [
  { id: 1, label: "Product Info", icon: Package },
  { id: 2, label: "Issue Details", icon: AlertTriangle },
  { id: 3, label: "Evidence", icon: Camera },
  { id: 4, label: "Review", icon: CheckCircle2 },
];

// ─── Step Components ─────────────────────────────────────────────────────────

function FieldLabel({ children, required }: { children: React.ReactNode; required?: boolean }) {
  return (
    <label className="block text-sm font-semibold text-gray-700 mb-1.5">
      {children}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
  );
}

function FieldInput({
  value,
  onChange,
  placeholder,
  type = "text",
  error,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  error?: string;
  disabled?: boolean;
}) {
  return (
    <>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          "w-full px-4 py-3 rounded-xl border bg-white text-gray-900 placeholder-gray-400",
          "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
          "transition-all text-sm disabled:opacity-60",
          error ? "border-red-400 bg-red-50" : "border-gray-200 hover:border-blue-300"
        )}
        max={type === "date" ? new Date().toISOString().split("T")[0] : undefined}
      />
      {error && <p className="text-red-500 text-xs mt-1 flex items-center gap-1"><Info className="w-3 h-3" />{error}</p>}
    </>
  );
}

// Step 1
function Step1ProductInfo({
  data,
  errors,
  onChange,
}: {
  data: FormData;
  errors: FieldError;
  onChange: (k: keyof FormData, v: any) => void;
}) {
  return (
    <div className="space-y-5">
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex gap-3">
        <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-blue-700">
          Please provide accurate product details. Barcode and product name are required.
        </p>
      </div>

      <div>
        <FieldLabel required>Product Name</FieldLabel>
        <FieldInput
          value={data.product_name}
          onChange={(v) => onChange("product_name", v)}
          placeholder="e.g. Amul Milk 500ml"
          error={errors.product_name}
        />
      </div>

      <div>
        <FieldLabel required>Barcode / SKU</FieldLabel>
        <FieldInput
          value={data.barcode}
          onChange={(v) => onChange("barcode", v)}
          placeholder="e.g. 8901234567890"
          error={errors.barcode}
        />
        <p className="text-xs text-gray-500 mt-1">Find on the product packaging label</p>
      </div>

      <div>
        <FieldLabel>Batch Number</FieldLabel>
        <FieldInput
          value={data.batch_number}
          onChange={(v) => onChange("batch_number", v)}
          placeholder="e.g. BATCH-2024-001 (if visible)"
          error={errors.batch_number}
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <FieldLabel>Purchase Date</FieldLabel>
          <FieldInput
            type="date"
            value={data.purchase_date}
            onChange={(v) => onChange("purchase_date", v)}
            error={errors.purchase_date}
          />
        </div>
        <div>
          <FieldLabel>Store Name</FieldLabel>
          <FieldInput
            value={data.store_name}
            onChange={(v) => onChange("store_name", v)}
            placeholder="e.g. Big Bazaar, D-Mart"
          />
        </div>
      </div>

      <div>
        <FieldLabel>Store Location / City</FieldLabel>
        <FieldInput
          value={data.store_location}
          onChange={(v) => onChange("store_location", v)}
          placeholder="e.g. Chennai, Tamil Nadu"
        />
      </div>
    </div>
  );
}

// Step 2
function Step2IssueInfo({
  data,
  errors,
  onChange,
}: {
  data: FormData;
  errors: FieldError;
  onChange: (k: keyof FormData, v: any) => void;
}) {
  return (
    <div className="space-y-5">
      <div>
        <FieldLabel required>Issue Type</FieldLabel>
        <div className="grid grid-cols-2 gap-2">
          {ISSUE_TYPES.map((type) => (
            <button
              key={type.value}
              type="button"
              onClick={() => onChange("report_type", type.value)}
              className={cn(
                "flex items-center gap-2 px-4 py-3 rounded-xl border text-sm font-medium transition-all text-left",
                data.report_type === type.value
                  ? "border-blue-500 bg-blue-50 text-blue-700 shadow-sm"
                  : "border-gray-200 bg-white text-gray-700 hover:border-blue-300 hover:bg-blue-50"
              )}
            >
              <span className="text-base">{type.emoji}</span>
              <span className="leading-tight">{type.label}</span>
            </button>
          ))}
        </div>
        {errors.report_type && (
          <p className="text-red-500 text-xs mt-1 flex items-center gap-1">
            <Info className="w-3 h-3" />{errors.report_type}
          </p>
        )}
      </div>

      <div>
        <FieldLabel required>Describe the Issue</FieldLabel>
        <textarea
          value={data.description}
          onChange={(e) => onChange("description", e.target.value)}
          placeholder="Please describe the problem in detail. What did you notice? When did you notice it? How did it affect the product?"
          rows={5}
          className={cn(
            "w-full px-4 py-3 rounded-xl border bg-white text-gray-900 placeholder-gray-400 resize-none",
            "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
            "transition-all text-sm leading-relaxed",
            errors.description ? "border-red-400 bg-red-50" : "border-gray-200 hover:border-blue-300"
          )}
        />
        <div className="flex items-center justify-between mt-1">
          {errors.description ? (
            <p className="text-red-500 text-xs flex items-center gap-1"><Info className="w-3 h-3" />{errors.description}</p>
          ) : (
            <p className="text-xs text-gray-500">Minimum 20 characters</p>
          )}
          <span className={cn(
            "text-xs",
            data.description.length < 20 ? "text-red-400" : "text-green-600"
          )}>
            {data.description.length}/500
          </span>
        </div>
      </div>
    </div>
  );
}

// Step 3
function Step3Evidence({
  data,
  errors,
  onChange,
}: {
  data: FormData;
  errors: FieldError;
  onChange: (k: keyof FormData, v: any) => void;
}) {
  const handleImageAdd = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const remaining = 5 - data.images.length;
    const toAdd = files.slice(0, remaining);

    const newImages = [...data.images, ...toAdd];
    const newPreviews = [...data.imagePreviews];

    toAdd.forEach((file) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        newPreviews.push(reader.result as string);
        onChange("imagePreviews", [...newPreviews]);
      };
      reader.readAsDataURL(file);
    });

    onChange("images", newImages);
    e.target.value = "";
  };

  const removeImage = (idx: number) => {
    const imgs = [...data.images];
    const prevs = [...data.imagePreviews];
    imgs.splice(idx, 1);
    prevs.splice(idx, 1);
    onChange("images", imgs);
    onChange("imagePreviews", prevs);
  };

  return (
    <div className="space-y-5">
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex gap-3">
        <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-amber-700">
          <p className="font-semibold mb-1">Evidence strengthens your report</p>
          <p>Photos of the defect, packaging, or batch number significantly increase the credibility of your report. Max 5 images.</p>
        </div>
      </div>

      {/* Upload Zone */}
      {data.images.length < 5 && (
        <label className="block cursor-pointer">
          <div className="border-2 border-dashed border-blue-300 hover:border-blue-500 bg-blue-50 hover:bg-blue-100 rounded-2xl p-8 text-center transition-all group">
            <Upload className="w-10 h-10 text-blue-400 group-hover:text-blue-600 mx-auto mb-3 transition-colors" />
            <p className="font-semibold text-gray-700 mb-1">Click to upload photos</p>
            <p className="text-sm text-gray-500">JPG, PNG, WEBP — Max 10MB each</p>
            <p className="text-xs text-blue-600 mt-2">{5 - data.images.length} slot{5 - data.images.length !== 1 ? "s" : ""} remaining</p>
          </div>
          <input
            type="file"
            className="hidden"
            accept="image/*"
            multiple
            onChange={handleImageAdd}
          />
        </label>
      )}

      {/* Image Previews */}
      {data.imagePreviews.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {data.imagePreviews.map((preview, idx) => (
            <div key={idx} className="relative group rounded-xl overflow-hidden bg-gray-100 aspect-square">
              <img
                src={preview}
                alt={`Evidence ${idx + 1}`}
                className="w-full h-full object-cover"
              />
              <button
                type="button"
                onClick={() => removeImage(idx)}
                className="absolute top-2 right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-md"
              >
                <X className="w-3.5 h-3.5" />
              </button>
              <div className="absolute bottom-0 left-0 right-0 bg-black/40 text-white text-xs py-1 px-2">
                Photo {idx + 1}
              </div>
            </div>
          ))}
        </div>
      )}

      {data.images.length === 0 && (
        <p className="text-center text-sm text-gray-500 italic py-2">
          No images added — Evidence is optional but recommended
        </p>
      )}

      {errors.images && (
        <p className="text-red-500 text-xs flex items-center gap-1">
          <Info className="w-3 h-3" />{errors.images}
        </p>
      )}
    </div>
  );
}

// Step 4 – Review
function Step4Review({ data }: { data: FormData }) {
  const issueLabel = ISSUE_TYPES.find((t) => t.value === data.report_type)?.label || data.report_type;

  return (
    <div className="space-y-4">
      <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex gap-3">
        <ShieldCheck className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-green-700 font-medium">
          Please review your report before submitting. Once submitted, it will be reviewed by our safety team.
        </p>
      </div>

      {/* Product Info */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-3 bg-gray-50 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 text-sm">
            <Package className="w-4 h-4 text-blue-600" /> Product Information
          </h3>
        </div>
        <div className="p-5 space-y-3">
          <ReviewRow label="Product Name" value={data.product_name} />
          <ReviewRow label="Barcode" value={data.barcode} mono />
          <ReviewRow label="Batch Number" value={data.batch_number || "Not provided"} />
          <ReviewRow label="Purchase Date" value={data.purchase_date || "Not provided"} />
          <ReviewRow label="Store" value={data.store_name ? `${data.store_name}${data.store_location ? `, ${data.store_location}` : ""}` : "Not provided"} />
        </div>
      </div>

      {/* Issue Info */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-3 bg-gray-50 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-amber-500" /> Issue Details
          </h3>
        </div>
        <div className="p-5 space-y-3">
          <ReviewRow label="Issue Type" value={issueLabel} />
          <div>
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</span>
            <p className="text-sm text-gray-900 mt-1 leading-relaxed bg-gray-50 rounded-lg p-3">
              {data.description}
            </p>
          </div>
        </div>
      </div>

      {/* Evidence */}
      <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div className="px-5 py-3 bg-gray-50 border-b border-gray-100">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2 text-sm">
            <Camera className="w-4 h-4 text-violet-500" /> Evidence
          </h3>
        </div>
        <div className="p-5">
          {data.imagePreviews.length === 0 ? (
            <p className="text-sm text-gray-400 italic">No images attached</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {data.imagePreviews.map((prev, i) => (
                <img
                  key={i}
                  src={prev}
                  alt={`Evidence ${i + 1}`}
                  className="w-20 h-20 rounded-lg object-cover border border-gray-200"
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ReviewRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex gap-3">
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider w-28 flex-shrink-0 pt-0.5">{label}</span>
      <span className={cn("text-sm text-gray-900", mono && "font-mono")}>{value}</span>
    </div>
  );
}

// ─── Success Screen ──────────────────────────────────────────────────────────

function SuccessScreen({ result, onViewReports }: { result: SubmissionResult; onViewReports: () => void }) {
  return (
    <div className="py-12 text-center">
      {/* Success animation */}
      <div className="relative mx-auto w-32 h-32 mb-8">
        <div className="absolute inset-0 bg-green-400 rounded-full opacity-20 animate-ping" />
        <div className="absolute inset-2 bg-green-500 rounded-full opacity-30 animate-ping animation-delay-150" />
        <div className="relative w-32 h-32 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center shadow-xl">
          <CheckCircle2 className="w-16 h-16 text-white" />
        </div>
      </div>

      <h2 className="text-3xl font-bold text-gray-900 mb-3">Thank You!</h2>
      <p className="text-lg text-gray-600 mb-8 max-w-sm mx-auto">
        Your report has been submitted successfully. Our safety team will review it shortly.
      </p>

      {/* Report details card */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 max-w-md mx-auto mb-8 text-left">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600" />
          Report Confirmation
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b border-gray-100">
            <span className="text-sm text-gray-500">Report ID</span>
            <span className="text-sm font-mono font-semibold text-gray-900 bg-gray-100 px-2 py-0.5 rounded-md">
              #{result.id.substring(0, 8).toUpperCase()}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-gray-100">
            <span className="text-sm text-gray-500">Submitted</span>
            <span className="text-sm text-gray-900">
              {new Date(result.created_at).toLocaleString("en-IN", {
                day: "numeric", month: "short", year: "numeric",
                hour: "2-digit", minute: "2-digit"
              })}
            </span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-sm text-gray-500">Status</span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
              Under Review
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          onClick={onViewReports}
          className="flex items-center justify-center gap-2 px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95"
        >
          <FileText className="w-5 h-5" />
          View My Reports
        </button>
        <a
          href="/community"
          className="flex items-center justify-center gap-2 px-8 py-3.5 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-xl border-2 border-gray-200 transition-all"
        >
          Back to Home
        </a>
      </div>
    </div>
  );
}

// ─── Main Report Page ─────────────────────────────────────────────────────────

export default function ReportPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<SubmissionResult | null>(null);

  const [formData, setFormData] = useState<FormData>({
    product_name: "",
    barcode: "",
    batch_number: "",
    purchase_date: "",
    store_name: "",
    store_location: "",
    report_type: "",
    description: "",
    images: [],
    imagePreviews: [],
  });

  const [errors, setErrors] = useState<FieldError>({});

  const updateField = (key: keyof FormData, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: "" }));
  };

  // ── Validation ──────────────────────────────────────────────────────────────

  const validateStep = (step: number): boolean => {
    const newErrors: FieldError = {};

    if (step === 1) {
      if (!formData.product_name.trim()) newErrors.product_name = "Product name is required";
      if (!formData.barcode.trim()) newErrors.barcode = "Barcode is required";
      if (formData.purchase_date) {
        const pd = new Date(formData.purchase_date);
        const today = new Date();
        today.setHours(23, 59, 59, 999);
        if (pd > today) newErrors.purchase_date = "Purchase date cannot be in the future";
      }
    }

    if (step === 2) {
      if (!formData.report_type) newErrors.report_type = "Please select an issue type";
      if (!formData.description.trim()) newErrors.description = "Description is required";
      else if (formData.description.trim().length < 20)
        newErrors.description = "Please describe the issue in at least 20 characters";
    }

    if (step === 3) {
      if (formData.images.length > 5) newErrors.images = "Maximum 5 images allowed";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((s) => Math.min(s + 1, 4));
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleBack = () => {
    setCurrentStep((s) => Math.max(s - 1, 1));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // ── Submission ──────────────────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!validateStep(4)) return;
    setSubmitting(true);
    setSubmitError(null);

    try {
      // We need a community user_id to submit a report.
      // Use a deterministic guest ID stored in localStorage.
      let userId = localStorage.getItem("community_user_id");
      if (!userId) {
        try {
          const guestEmail = `guest-${Date.now()}@community.pgn`;
          const userRes = await apiFetch<any>("/community/users", {
            method: "POST",
            body: JSON.stringify({
              full_name: "Community Reporter",
              email: guestEmail,
            }),
          });
          const userObj = userRes.data || userRes;
          userId = userObj.id;
          localStorage.setItem("community_user_id", userId!);
        } catch {
          // If user creation fails, fall back to a placeholder
          userId = "00000000-0000-0000-0000-000000000001";
        }
      }

      // Build report payload
      const images = formData.imagePreviews.map((url, i) => ({
        image_url: url.substring(0, 500), // trim data URL for API
      }));

      const purchaseLocation = [formData.store_name.trim(), formData.store_location.trim()]
        .filter(Boolean)
        .join(" - ");

      const reportPayload: any = {
        user_id: userId,
        barcode: formData.barcode.trim(),
        batch_number: formData.batch_number.trim() || "UNKNOWN",
        product_name: formData.product_name.trim(),
        report_type: formData.report_type,
        severity: "MEDIUM", // Default severity required by backend schema
        description: formData.description.trim(),
        purchase_location: purchaseLocation || null,
        purchase_date: formData.purchase_date || null,
        images: images.slice(0, 5),
      };

      const res = await apiFetch<any>("/community/reports", {
        method: "POST",
        body: JSON.stringify(reportPayload),
      });

      const reportObj = res.data || res;

      // Store report ID in localStorage for My Reports
      const existingReports = JSON.parse(localStorage.getItem("my_report_ids") || "[]");
      existingReports.unshift(reportObj.id);
      localStorage.setItem("my_report_ids", JSON.stringify(existingReports.slice(0, 50)));

      setSubmissionResult({
        id: reportObj.id,
        created_at: reportObj.created_at,
        status: reportObj.status,
        barcode: reportObj.barcode,
      });
      setSubmitted(true);
    } catch (err: any) {
      let msg = "We couldn't submit your report. Please try again.";
      if (err.message) {
        if (err.message.includes("409")) msg = "A similar report was already submitted within the last 24 hours.";
        else if (err.message.includes("404")) msg = "User account not found. Please try again.";
        else msg = err.message;
      }
      setSubmitError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  // ── Success Screen ──────────────────────────────────────────────────────────

  if (submitted && submissionResult) {
    return (
      <div className="py-8">
        <div className="max-w-2xl mx-auto">
          <SuccessScreen
            result={submissionResult}
            onViewReports={() => router.push("/community/my-reports")}
          />
        </div>
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  const StepIcon = STEPS[currentStep - 1].icon;

  return (
    <div className="py-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Report a Product</h1>
          <p className="text-gray-500 mt-2">Complete all steps to submit your safety report</p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-between mb-8 px-2">
          {STEPS.map((step, i) => {
            const Icon = step.icon;
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            return (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center gap-1">
                  <div
                    className={cn(
                      "w-10 h-10 rounded-full flex items-center justify-center transition-all",
                      isCompleted ? "bg-green-500 text-white shadow-md" :
                      isCurrent ? "bg-blue-600 text-white shadow-md shadow-blue-200" :
                      "bg-gray-200 text-gray-400"
                    )}
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <Icon className="w-5 h-5" />
                    )}
                  </div>
                  <span className={cn(
                    "text-xs font-medium hidden sm:block",
                    isCurrent ? "text-blue-700" : isCompleted ? "text-green-600" : "text-gray-400"
                  )}>
                    {step.label}
                  </span>
                </div>
                {i < STEPS.length - 1 && (
                  <div className={cn(
                    "flex-1 h-0.5 mx-2 transition-all",
                    currentStep > step.id ? "bg-green-400" : "bg-gray-200"
                  )} />
                )}
              </div>
            );
          })}
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          {/* Card Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <StepIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-blue-200 text-xs font-medium">STEP {currentStep} OF 4</p>
                <h2 className="text-white font-bold text-lg">{STEPS[currentStep - 1].label}</h2>
              </div>
            </div>
            {/* Progress bar */}
            <div className="mt-4 h-1.5 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-500"
                style={{ width: `${(currentStep / 4) * 100}%` }}
              />
            </div>
          </div>

          {/* Form Body */}
          <div className="p-6">
            {currentStep === 1 && (
              <Step1ProductInfo data={formData} errors={errors} onChange={updateField} />
            )}
            {currentStep === 2 && (
              <Step2IssueInfo data={formData} errors={errors} onChange={updateField} />
            )}
            {currentStep === 3 && (
              <Step3Evidence data={formData} errors={errors} onChange={updateField} />
            )}
            {currentStep === 4 && (
              <Step4Review data={formData} />
            )}

            {/* Submit Error */}
            {submitError && currentStep === 4 && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-700 text-sm">Submission Failed</p>
                  <p className="text-red-600 text-sm mt-0.5">{submitError}</p>
                </div>
              </div>
            )}
          </div>

          {/* Navigation Footer */}
          <div className="px-6 pb-6 flex justify-between gap-4">
            <button
              type="button"
              onClick={handleBack}
              disabled={currentStep === 1 || submitting}
              className="flex items-center gap-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>

            {currentStep < 4 ? (
              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-2 px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95"
              >
                Continue
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={handleSubmit}
                disabled={submitting}
                className="flex items-center gap-2 px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    Submit Report
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Security note */}
        <p className="text-center text-xs text-gray-400 mt-4 flex items-center justify-center gap-1">
          <Lock className="w-3 h-3" />
          Your report is confidential and will only be used for safety purposes
        </p>
      </div>
    </div>
  );
}

// Need lock icon
function Lock({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}
