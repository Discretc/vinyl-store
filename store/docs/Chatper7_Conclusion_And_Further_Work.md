# Chapter 7 Conclusion and Further Work

## 7.1 Summary

This project set out to build a multi-vendor online shopping platform for vinyl records using Django, covering six requirement blocks (A, B, F, T, U, X). The final system delivers a complete shopping experience — customers can browse a searchable catalogue, view detailed product pages with multiple images, manage a persistent cart, and check out selectively from multiple vendors in a single session. Orders follow a five-stage lifecycle with full status history, and customers can cancel items or request refunds directly from their order page.

On the vendor side, each seller operates within their own scoped portal where they manage products, images, promotions, and incoming orders without visibility into other vendors' data. Time-bound promotional pricing is applied automatically across the platform, and wishlisted customers are notified when discounts become available. A purchase-gated review system with star ratings and optional photos supports community-driven product discovery, while logged search queries and click history give vendors insight into customer demand.

The interface is responsive across desktop and mobile, with role-specific layouts, colour-coded status indicators, notification badges, and accessibility considerations including ARIA attributes and focus styling. Overall, the platform functions as a cohesive multi-vendor marketplace that integrates shopping, vendor management, and customer engagement features into a single application.

## 7.2 Limitations and Further Work

Several limitations remain as opportunities for future work. Verification was performed manually (Chapter 6); converting these into automated unit and integration tests would guard against regressions. The system lacks a real payment gateway — integrating Stripe or PayPal would make order creation conditional on successful payment. Notifications are in-application only; email and push notification delivery would improve engagement. Security measures suit a coursework context but production deployment would require HTTPS enforcement, rate limiting, improved upload validation, and safer DOM rendering. Search uses substring matching; full-text search, recommendations (Block S), and category filtering (Block C) would strengthen discovery. Vendor analytics are limited to basic counts and could be extended toward Block V capabilities. Finally, accessibility was not formally audited against WCAG, and internationalisation was not implemented.

In summary, the delivered system meets the six selected blocks and provides a working multi-vendor platform. These limitations are realistic extensions rather than specification gaps, and the existing architecture supports addressing them incrementally.