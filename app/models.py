from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for status fields
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    CASH_ON_DELIVERY = "cod"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    addresses: List["Address"] = Relationship(back_populates="user")
    cart_items: List["CartItem"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: Optional[str] = Field(default=None, max_length=500)
    icon_name: str = Field(max_length=50)  # Icon identifier for UI
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    __tablename__ = "products"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    price: Decimal = Field(decimal_places=2, ge=0)
    original_price: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    stock_quantity: int = Field(ge=0, default=0)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    sku: str = Field(max_length=100, unique=True)
    weight: Optional[Decimal] = Field(default=None, decimal_places=3, ge=0)  # in kg
    dimensions: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))  # {width, height, depth}
    specifications: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    images: List[str] = Field(default=[], sa_column=Column(JSON))  # List of image URLs
    rating: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    is_featured: bool = Field(default=False)
    is_active: bool = Field(default=True)
    category_id: int = Field(foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    category: Category = Relationship(back_populates="products")
    cart_items: List["CartItem"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


class Address(SQLModel, table=True):
    __tablename__ = "addresses"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    label: str = Field(max_length=50)  # e.g., "Home", "Office"
    recipient_name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    address_line_1: str = Field(max_length=200)
    address_line_2: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(max_length=100)
    province: str = Field(max_length=100)
    postal_code: str = Field(max_length=10)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="addresses")
    orders: List["Order"] = Relationship(back_populates="shipping_address")


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="cart_items")
    product: Product = Relationship(back_populates="cart_items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, max_length=50)
    user_id: int = Field(foreign_key="users.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    subtotal: Decimal = Field(decimal_places=2, ge=0)
    shipping_cost: Decimal = Field(decimal_places=2, ge=0, default=Decimal("0"))
    tax_amount: Decimal = Field(decimal_places=2, ge=0, default=Decimal("0"))
    discount_amount: Decimal = Field(decimal_places=2, ge=0, default=Decimal("0"))
    total_amount: Decimal = Field(decimal_places=2, ge=0)
    payment_method: PaymentMethod
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    shipping_address_id: int = Field(foreign_key="addresses.id")
    notes: Optional[str] = Field(default=None, max_length=500)
    tracking_number: Optional[str] = Field(default=None, max_length=100)
    shipped_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="orders")
    shipping_address: Address = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(decimal_places=2, ge=0)
    total_price: Decimal = Field(decimal_places=2, ge=0)
    product_snapshot: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Product details at time of order

    # Relationships
    order: Order = Relationship(back_populates="order_items")
    product: Product = Relationship(back_populates="order_items")


class Banner(SQLModel, table=True):
    __tablename__ = "banners"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    image_url: str = Field(max_length=500)
    link_url: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    name: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


class CategoryCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon_name: str = Field(max_length=50)
    sort_order: int = Field(default=0)


class CategoryUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon_name: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = Field(default=None)
    sort_order: Optional[int] = Field(default=None)


class ProductCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    price: Decimal = Field(decimal_places=2, ge=0)
    original_price: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    stock_quantity: int = Field(ge=0)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    sku: str = Field(max_length=100)
    weight: Optional[Decimal] = Field(default=None, decimal_places=3, ge=0)
    dimensions: Optional[Dict[str, Any]] = Field(default=None)
    specifications: Dict[str, Any] = Field(default={})
    images: List[str] = Field(default=[])
    is_featured: bool = Field(default=False)
    category_id: int


class ProductUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    original_price: Optional[Decimal] = Field(default=None, decimal_places=2, ge=0)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    brand: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    weight: Optional[Decimal] = Field(default=None, decimal_places=3, ge=0)
    dimensions: Optional[Dict[str, Any]] = Field(default=None)
    specifications: Optional[Dict[str, Any]] = Field(default=None)
    images: Optional[List[str]] = Field(default=None)
    is_featured: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    category_id: Optional[int] = Field(default=None)


class AddressCreate(SQLModel, table=False):
    label: str = Field(max_length=50)
    recipient_name: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    address_line_1: str = Field(max_length=200)
    address_line_2: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(max_length=100)
    province: str = Field(max_length=100)
    postal_code: str = Field(max_length=10)
    is_default: bool = Field(default=False)


class AddressUpdate(SQLModel, table=False):
    label: Optional[str] = Field(default=None, max_length=50)
    recipient_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    address_line_1: Optional[str] = Field(default=None, max_length=200)
    address_line_2: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=10)
    is_default: Optional[bool] = Field(default=None)


class CartItemCreate(SQLModel, table=False):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(SQLModel, table=False):
    quantity: int = Field(ge=1)


class OrderCreate(SQLModel, table=False):
    payment_method: PaymentMethod
    shipping_address_id: int
    notes: Optional[str] = Field(default=None, max_length=500)


class OrderItemCreate(SQLModel, table=False):
    product_id: int
    quantity: int = Field(ge=1)


class BannerCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    image_url: str = Field(max_length=500)
    link_url: Optional[str] = Field(default=None, max_length=500)
    sort_order: int = Field(default=0)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)


class BannerUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    subtitle: Optional[str] = Field(default=None, max_length=300)
    image_url: Optional[str] = Field(default=None, max_length=500)
    link_url: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)
    sort_order: Optional[int] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)


# Response schemas for API
class ProductResponse(SQLModel, table=False):
    id: int
    name: str
    description: str
    price: Decimal
    original_price: Optional[Decimal]
    stock_quantity: int
    brand: Optional[str]
    model: Optional[str]
    sku: str
    weight: Optional[Decimal]
    dimensions: Optional[Dict[str, Any]]
    specifications: Dict[str, Any]
    images: List[str]
    rating: Optional[Decimal]
    review_count: int
    is_featured: bool
    is_active: bool
    category_id: int
    category_name: str
    created_at: str  # ISO format
    updated_at: str  # ISO format


class OrderResponse(SQLModel, table=False):
    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    shipping_cost: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    notes: Optional[str]
    tracking_number: Optional[str]
    shipped_at: Optional[str]  # ISO format
    delivered_at: Optional[str]  # ISO format
    created_at: str  # ISO format
    updated_at: str  # ISO format
    shipping_address: AddressCreate
    order_items: List[Dict[str, Any]]


class CartSummary(SQLModel, table=False):
    items_count: int
    total_amount: Decimal
    items: List[Dict[str, Any]]
