// Shipment booking contract: types, parsing, and admission rules.
// Pure module: no I/O, no dependencies.

export const CONTRACT_VERSION = 3;

export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

export function object(value: unknown, path: string): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new Error(`${path} must be an object`);
  }

  return value as Record<string, unknown>;
}

export function text(record: Record<string, unknown>, key: string, path: string): string {
  const value = record[key];

  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`${path}.${key} must be a non-empty string, got ${JSON.stringify(value)}`);
  }

  return value;
}

export function number(record: Record<string, unknown>, key: string, path: string): number {
  const value = record[key];

  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`${path}.${key} must be a number, got ${JSON.stringify(value)}`);
  }

  return value;
}

export function bool(record: Record<string, unknown>, key: string, path: string): boolean {
  const value = record[key];

  if (typeof value !== 'boolean') {
    throw new Error(`${path}.${key} must be a boolean, got ${JSON.stringify(value)}`);
  }

  return value;
}

export function date(record: Record<string, unknown>, key: string, path: string): Date {
  const raw = text(record, key, path);
  const parsed = new Date(raw);

  if (Number.isNaN(parsed.getTime())) {
    throw new Error(`${path}.${key} must be an ISO date, got ${raw}`);
  }

  return parsed;
}

export function keys(record: Record<string, unknown>, allowed: readonly string[], path: string): void {
  for (const key of Object.keys(record)) {
    if (!allowed.includes(key)) {
      throw new Error(`${path} has unknown key ${key}`);
    }
  }
}

export interface Booking {
  id: string;
  version: number;
  createdAt: Date;
  customer: {
    id: string;
    name: string;
    email: string;
    phone: string;
    tier: string;
    verified: boolean;
  };
  pickup: {
    street: string;
    city: string;
    postcode: string;
    country: string;
    window: { from: Date; to: Date };
  };
  dropoff: {
    street: string;
    city: string;
    postcode: string;
    country: string;
    window: { from: Date; to: Date };
  };
  parcel: {
    weightGrams: number;
    lengthMm: number;
    widthMm: number;
    heightMm: number;
    fragile: boolean;
    declaredValueCents: number;
  };
  options: {
    insured: boolean;
    signatureRequired: boolean;
    express: boolean;
  };
}

export type Decision = { admitted: true } | { admitted: false; reasons: string[] };

const BOOKING_KEYS = ['id', 'version', 'createdAt', 'customer', 'pickup', 'dropoff', 'parcel', 'options'];
const CUSTOMER_KEYS = ['id', 'name', 'email', 'phone', 'tier', 'verified'];
const ADDRESS_KEYS = ['street', 'city', 'postcode', 'country', 'window'];
const WINDOW_KEYS = ['from', 'to'];
const PARCEL_KEYS = ['weightGrams', 'lengthMm', 'widthMm', 'heightMm', 'fragile', 'declaredValueCents'];
const OPTION_KEYS = ['insured', 'signatureRequired', 'express'];

function window(value: unknown, path: string): { from: Date; to: Date } {
  const data = object(value, path);
  keys(data, WINDOW_KEYS, path);

  return { from: date(data, 'from', path), to: date(data, 'to', path) };
}

function address(value: unknown, path: string): Booking['pickup'] {
  const data = object(value, path);
  keys(data, ADDRESS_KEYS, path);

  return {
    street: text(data, 'street', path),
    city: text(data, 'city', path),
    postcode: text(data, 'postcode', path),
    country: text(data, 'country', path),
    window: window(data.window, `${path}.window`),
  };
}

export function parseBooking(raw: string): Booking {
  const data = object(JSON.parse(raw), 'booking');
  keys(data, BOOKING_KEYS, 'booking');
  const customer = object(data.customer, 'booking.customer');
  keys(customer, CUSTOMER_KEYS, 'booking.customer');
  const parcel = object(data.parcel, 'booking.parcel');
  keys(parcel, PARCEL_KEYS, 'booking.parcel');
  const options = object(data.options, 'booking.options');
  keys(options, OPTION_KEYS, 'booking.options');

  return {
    id: text(data, 'id', 'booking'),
    version: number(data, 'version', 'booking'),
    createdAt: date(data, 'createdAt', 'booking'),
    customer: {
      id: text(customer, 'id', 'booking.customer'),
      name: text(customer, 'name', 'booking.customer'),
      email: text(customer, 'email', 'booking.customer'),
      phone: text(customer, 'phone', 'booking.customer'),
      tier: text(customer, 'tier', 'booking.customer'),
      verified: bool(customer, 'verified', 'booking.customer'),
    },
    pickup: address(data.pickup, 'booking.pickup'),
    dropoff: address(data.dropoff, 'booking.dropoff'),
    parcel: {
      weightGrams: number(parcel, 'weightGrams', 'booking.parcel'),
      lengthMm: number(parcel, 'lengthMm', 'booking.parcel'),
      widthMm: number(parcel, 'widthMm', 'booking.parcel'),
      heightMm: number(parcel, 'heightMm', 'booking.parcel'),
      fragile: bool(parcel, 'fragile', 'booking.parcel'),
      declaredValueCents: number(parcel, 'declaredValueCents', 'booking.parcel'),
    },
    options: {
      insured: bool(options, 'insured', 'booking.options'),
      signatureRequired: bool(options, 'signatureRequired', 'booking.options'),
      express: bool(options, 'express', 'booking.options'),
    },
  };
}

const MAX_WEIGHT = 30000;
const MAX_SIDE = 1200;
const MAX_UNINSURED_VALUE = 50000;
const EXPRESS_COUNTRIES = ['DE', 'NL', 'BE', 'AT'];

export function admit(booking: Booking, now: Date): Decision {
  const reasons: string[] = [];

  if (booking.version !== CONTRACT_VERSION) {
    reasons.push(`unsupported version ${booking.version}`);
  }

  if (!booking.customer.verified) {
    reasons.push('customer is not verified');
  }

  const p = booking.parcel;

  if (p.weightGrams > MAX_WEIGHT) {
    reasons.push('parcel is too heavy');
  }

  if (Math.max(p.lengthMm, p.widthMm, p.heightMm) > MAX_SIDE) {
    reasons.push('parcel is too large');
  }

  if (p.declaredValueCents > MAX_UNINSURED_VALUE && !booking.options.insured) {
    reasons.push('high-value parcel must be insured');
  }

  if (booking.options.express && !EXPRESS_COUNTRIES.includes(booking.dropoff.country)) {
    reasons.push('express is not available for the destination');
  }

  if (booking.pickup.window.to <= now) {
    reasons.push('pickup window has passed');
  }

  if (booking.pickup.window.from >= booking.pickup.window.to) {
    reasons.push('pickup window is empty');
  }

  if (booking.dropoff.window.from < booking.pickup.window.from) {
    reasons.push('dropoff window starts before pickup');
  }

  if (reasons.length > 0) {
    return { admitted: false, reasons };
  }

  return { admitted: true };
}

export function flag(booking: Booking): boolean {
  return booking.parcel.fragile && !booking.options.signatureRequired;
}
