# Chapter 6 Software Quality

## 6.1 Software Verification

The group used a mainly manual, requirement-based verification approach. Since the codebase does not include a developed automated test suite in `store/tests.py`, testing relied on debugging, repeated scenario execution, and direct inspection of database results and browser behaviour, with cross-checking between group members when integrated workflows were demonstrated.

The testing approach combined four practical layers: debugging during implementation to trace logic errors and confirm state transitions; functional tests to verify stock reductions, price calculations, and validation rules; integration tests covering end-to-end workflows such as customer registration through to vendor order processing; and acceptance-style checks comparing implemented features against the selected requirement blocks A, B, F, T, U, and X.

Test cases focused on non-trivial business rules rather than isolated page loading. Checkout testing confirmed that only selected cart items were converted to order items, that paid prices reflected active promotions, that stock was reduced correctly, and that vendor notifications were generated. Order-processing tests verified that vendors could only manage their own store's items and that status histories were appended rather than overwritten.

Requirement-based tests were especially important for features that only become meaningful in combination. Promotional pricing was checked for consistency across the home page, product listing, cart, checkout, and wishlist. User-generated content was verified by confirming that only customers with a purchase record could post reviews and that deleting a review removed the associated photo file. Major functions were also tested with invalid data: missing fields, mismatched passwords, out-of-range quantities, invalid discount percentages, and ineligible refund statuses.

The project seeding command provided a consistent baseline of customers, vendors, products, promotions, and reviews for multi-vendor scenarios. Edge-case data such as zero-stock products, expired promotions, and customers with no purchase history was added manually. The main limitation of the verification process is weak automated regression coverage; converting the current manual scenarios into automated unit and integration tests remains the most important future quality improvement.

## 6.2 Security

Security was addressed through framework-supported protection, input validation, and ownership checks. Passwords are hashed using Django's utilities and never stored in plain text. Server-side sessions maintain authentication state, and role-specific checks guard every sensitive operation: customer-only functions require a valid customer session, and vendor-only functions require a valid vendor session.

Ownership verification prevents insecure direct object reference attacks. Vendors can only modify products, promotions, and order items belonging to their own store, and customers can only access their own orders, cancellations, and reviews. Input validation combines Django model constraints with view-level checks on quantities, prices, ratings, discount ranges, and promotion date order. Uploaded review photos are resized on the server before storage to standardize content.

Cross-site scripting risk is reduced by Django's template system, which escapes output by default. One residual risk exists in the notification dropdown, which uses JavaScript `innerHTML` to render messages that may include user-controlled values such as product names. A more robust approach would use DOM text-content methods or a client-side escaping function. CSRF protection is provided through `CsrfViewMiddleware` with tokens in all forms and AJAX requests, and `XFrameOptionsMiddleware` prevents clickjacking. All state-changing endpoints are restricted to POST using the `@require_POST` decorator across approximately twenty view functions.

The current configuration has `DEBUG` enabled and `ALLOWED_HOSTS` set broadly, which is acceptable for coursework but not for a public deployment. A production version would require HTTPS, tightened host settings, disabled debug mode, stronger upload restrictions, and structured logging. Overall, the security approach addresses the main application-level threats appropriately for a coursework system, and the remaining gaps relate to production hardening rather than missing basic measures.

## 6.3 Reflection on User Experience

The interface was designed for customers and vendors with varying levels of digital confidence. It uses familiar e-commerce structures — search and filtering, product cards, cart summaries, order history, and clear action buttons — and conventional navigation labels such as Browse, Wishlist, Orders, and Dashboard. The responsive layout supports both mobile customers and desktop vendors, and the separation of customer and vendor workflows prevents users from being overloaded with irrelevant actions.

Several decisions support accessibility. The page structure is readable and consistent, form controls have visible focus styling, and ARIA attributes such as `aria-label` and `aria-expanded` are applied to mobile navigation and notification controls. Important actions are presented as explicit buttons and forms rather than gesture-only interactions, and feedback through alerts and status labels reduces ambiguity after each action.

The system does not claim full WCAG 2.1 compliance, and no formal assistive-technology evaluation was conducted. Further improvements would include comprehensive keyboard-only testing, reduced-motion support, stronger colour-contrast auditing, and screen-reader testing across key workflows. User experience testing was based on internal walkthroughs rather than external user studies, so broader usability validation across different age groups, backgrounds, and abilities remains future work.

## 6.4 Other Quality Attributes

### 6.4.1 Maintainability

The system contains many interconnected workflows where a change in one area can affect other areas, particularly pricing and order lifecycle logic. Current design choices support maintainability through clear Django model structures, separated URL routing, isolated templates, and shared helper logic for operations such as promotion expiry and photo resizing. The main weakness is that a large amount of business logic is concentrated in `views.py`. Future improvements should extract repeated logic into service modules and add automated regression tests around the most sensitive business rules.

### 6.4.2 Reliability

Core operations including checkout, stock adjustment, promotion pricing, review eligibility, and refund handling demand high reliability because errors in these areas would undermine user trust quickly. The project supports reliability by storing order-item status changes as separate history records rather than overwriting them, and by preserving the paid price at order creation time. Future work should introduce database transactions around critical multi-step operations and expand error logging to support faster diagnosis of unexpected failures.

### 6.4.3 Performance

The system targets responsive everyday performance under class-demonstration usage rather than enterprise-scale throughput. Query performance is supported through `select_related` and `prefetch_related`, desktop pagination, and mobile infinite scrolling. Further improvements for larger deployments would include indexing frequently searched fields, caching high-traffic queries, and profiling vendor dashboard aggregation queries.

Overall, these non-functional qualities determine whether the system remains dependable and extensible beyond initial implementation. The project should be judged not only by whether features exist but also by whether the code and architecture can support their continued correct use.
