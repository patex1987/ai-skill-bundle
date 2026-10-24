// Import the logger
import { logger } from './logger';

// This function adds tax
/**
 * Adds tax.
 * @param {number} amount - the amount
 * @param {number} rate - the rate
 * @returns {number} the result
 */
export function addTax(amount: number, rate: number): number {
  // Multiply amount by one plus the rate
  const total = amount * (1 + rate);
  // Log it
  logger.debug('total', total);
  // const old = amount + amount * rate;
  // Return the total
  return Math.round(total);
}
