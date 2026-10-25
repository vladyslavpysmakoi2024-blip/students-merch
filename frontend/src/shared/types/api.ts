export interface User {
  id: number;
  email: string;
  first_name: string | null;
  last_name: string | null;
  fathers_name?: string | null;
  phone_number: string | null;
  city?: string | null;
  street?: string | null;
  house_number?: string | null;
  avatar_url?: string | null;
  completed_survey: boolean;
  is_admin: boolean;
}

export interface ClothingItem {
  id: number;
  name: string | null;
  type: string | null;
  color: string | null;
  color_name?: string | null;
  size?: string | null;
  composition?: string | null;
  price: number | string;
  quantity?: number | null;
  photo?: string | null;
  photos?: string[] | null;
  texture?: string | null;
}

export interface CartItem {
  cart_id: number;
  product_id: number;
  name: string;
  type?: string | null;
  color?: string | null;
  color_name?: string | null;
  size?: string | null;
  price: number;
  quantity: number;
  photo?: string | null;
  photos?: string[] | null;
}

export interface FavoriteItem {
  id: number;
  clothing: ClothingItem | null;
}

export interface OrderContentItem {
  id?: number;
  quantity: number;
  clothing: ClothingItem;
}

export interface OrderItem {
  id: number;
  price: number | string;
  date?: string | null;
  status?: string;
  delivery_company?: string | null;
  delivery_type?: string | null;
  postal_number?: string | null;
  items_count?: number;
  user?: User | null;
  order_content?: OrderContentItem[];
}

export interface OrderReceiptItem {
  name: string;
  type?: string | null;
  size?: string | null;
  quantity?: number;
  price: number | string;
  total?: number | string;
  photo?: string | null;
}

export interface OrderReceipt {
  order_id: number;
  receipt_number?: string;
  store_name?: string;
  store_address?: string;
  created_at?: string;
  payment_method?: string;
  monobank_receipt_url?: string | null;
  delivery_company?: string | null;
  postal_number?: string | null;
  invoice_id?: string | null;
  subtotal?: number | string;
  total_amount?: number | string;
  customer?: {
    name?: string | null;
    phone?: string | null;
    city?: string | null;
    street?: string | null;
    house_number?: string | null;
  } | null;
  items?: OrderReceiptItem[];
}

export interface PromoItem {
  id: number;
  promo: string;
  discount_percent: number | string;
  date_start: string;
  date_end: string;
}

export interface SurveyAnswer {
  id: string;
  title: string;
  type: "select" | "multiselect" | "opentext";
  value: string | string[];
}

export interface SurveyPackagePiece {
  id: string | number;
  name: string;
  color: string;
  photo?: string | null;
  photos?: string[] | null;
}

export interface SurveyPackageItem {
  id: string;
  tshirt: SurveyPackagePiece;
  tote: SurveyPackagePiece;
  price: number;
  discountPercent: number;
  discountedPrice: number;
}

export interface SurveyResponseData {
  id?: number;
  answers: SurveyAnswer[];
  assigned_package_id?: string | null;
  is_package_confirmed?: boolean;
  package?: SurveyPackageItem | null;
}
