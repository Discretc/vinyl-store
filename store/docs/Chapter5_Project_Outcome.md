# Chapter 5 Project Outcome

## 5.1 Overview of the Delivered System

The final system is a multi-vendor online shopping platform for vinyl records. It was developed as a web-based e-commerce application that supports customer shopping activities, vendor shop management, order processing, product promotion, and user engagement features within one integrated system. The project was implemented with Django, a relational database, server-side session management, and a responsive web interface for both customer-facing and vendor-facing workflows.

According to the system specification, the project selected the following requirement blocks:

- Basic requirement Block A: Basic online shopping functions
- Basic requirement Block B: Multiple product photos and basic order processing
- Basic requirement Block F: Multiple vendors and shops
- Further requirement Block T: User-generated content
- Further requirement Block U: Wishlist and promotional pricing strategy
- Further requirement Block X: User experience (UX) design

The completed system is not only a prototype of isolated pages. It supports an end-to-end shopping process from product discovery, product review, cart management, checkout, and order tracking, to vendor-side catalogue maintenance and order handling. In this chapter, the system is described in terms of the main non-trivial outcomes of the project rather than as a step-by-step user guide. Simple operations such as account login can be shown more efficiently in the demonstration video.

Suggested figure placement:

- Figure 5.1 Main storefront showing search, product listing, and shop information
- Figure 5.2 Product detail page with image gallery, pricing, wishlist, and review section
- Figure 5.3 Cart and checkout process
- Figure 5.4 Vendor dashboard and product management interface
- Figure 5.5 Vendor order processing page with status update and refund handling

When preparing the figures, screenshots should be cropped so that text remains readable when printed on A4 paper. It is better to use fewer, larger screenshots with clear callouts than many small screenshots.

## 5.2 Customer-Side Transaction Flow

One of the main outcomes of the project is a complete customer shopping flow that connects several requirement blocks into one coherent transaction. The storefront allows anonymous visitors to browse products, search the catalogue, and open product detail pages before login. After authentication, customers can continue to use shopping functions that require personal data persistence, including shopping cart management, checkout, order history, wishlist, and review submission.

### 5.2.1 Product Discovery and Catalogue Browsing

The system provides a searchable product catalogue presented in a responsive grid layout. Each product card shows the product name, price, image, store information, rating summary, and stock condition. Customers can search products by name and description, filter products by store, and narrow results by price range. This satisfies the core browsing and search expectations in Block A while also giving the platform enough scale to support multiple shops in Block F.

The home page itself is structured to support different shopping intentions. It separates products into an "On Sale Now" section, which highlights items with currently active promotions, and a "Featured Products" section for general catalogue visibility. This gives returning visitors immediate access to current deals while also showcasing the broader catalogue, rather than presenting a single undifferentiated list.

The implementation was designed to make browsing efficient rather than merely functional. On larger screens, the catalogue supports conventional pagination, while on smaller screens the system switches to infinite scroll, where additional products are loaded automatically as the customer scrolls down. This dual-mode approach is an important outcome of the project because it shows that the storefront was designed around realistic product exploration rather than around static page display.

Suggested figure placement:

- Figure 5.1 Storefront search and filtering across multiple products and shops

### 5.2.2 Product Detail Presentation

The product detail page is one of the most important pages in the system because it combines information from several selected requirement blocks. For each product, the system displays a richer product description, multiple product photos, current pricing, discount information when a promotion is active, rating information, stock availability, and the associated vendor shop. Customers can also add the product to the cart, add or remove it from the wishlist, and submit reviews if they have previously purchased it.

This page demonstrates the outcome of Block B particularly clearly. Instead of a single thumbnail image, each product can have multiple photos, and the page includes a product image gallery with a main display area and selectable supporting images. This improves the realism of the shopping experience and makes the system more suitable for media-rich retail presentation.

The same page also demonstrates the integration of Blocks T and U. User-generated reviews and ratings are displayed together with the product, while promotional pricing and wishlist actions are available in the same interface. As a result, the product detail page functions as a central point where browsing, trust-building, and conversion-oriented features meet.

Suggested figure placement:

- Figure 5.2 Product detail page showing multiple photos, active discount, wishlist control, and customer reviews

### 5.2.3 Shopping Cart and Checkout

The cart and checkout flow delivers the core transaction required in Block A. Customers can add products to the cart, revise quantities, remove items, and review calculated subtotals and totals before checkout. Cart data is stored on the server side, so the customer experience persists across sessions instead of depending only on the browser state.

A notable implementation detail is selective checkout. Rather than forcing the customer to check out the entire cart at once, the cart page provides a checkbox next to each item. Customers can select a subset of items to purchase while the remaining items stay in the cart for a future transaction. A select-all toggle is also provided, and the displayed subtotal recalculates dynamically based on the current selection. This is a non-trivial feature because it requires the checkout process to accept an arbitrary subset of cart items, create order records only for the selected products, and leave unselected items untouched.

At checkout, the customer confirms the shipping address and submits the selected items to create an order. The system then records the order, creates corresponding order items, stores the paid price for historical accuracy, and updates stock quantities. This part of the project is significant because it moves beyond simple page navigation and implements the underlying business logic needed for a working online shopping system.

The checkout flow also integrates promotional pricing. If a product has an active promotion, the discounted price is reflected in the cart and in the final order calculation. This means the final system outcome is not just a static cart, but a cart that reflects current sales strategy and order value accurately.

Suggested figure placement:

- Figure 5.3 Cart page and checkout summary with promotional pricing applied

### 5.2.4 Order History, Order Detail, and Customer Actions

After checkout, the system allows customers to review their order history and inspect the detail of each order. Order records show the order identifier, date, shipping address, total value, and item-level pricing information. The order history page also supports filtering by status so that customers can quickly focus on orders that are still being processed or have already been completed.

This part of the project addresses Block B by implementing a real order-status workflow. Each order item stores a history of status changes, and the customer can see not only the current status but also the sequence of updates over time. The project defines and uses a multi-stage status model including Processing, Holding, Shipping, Completed, and Cancelled. This is more substantial than merely storing a single text field because it captures the operational progress of the order.

Because a single order can contain items from different vendors, each progressing at its own pace, the system also computes an aggregate order-level status. If all items share the same status, the order displays that status. If all items have been cancelled, the order shows Cancelled. If items have different active statuses, the order is labelled Mixed. This aggregate logic is useful because it gives customers an at-a-glance summary on the order history page while the full per-item breakdown remains available on the order detail page.

The customer-facing order pages also support actions that affect the order lifecycle. Depending on the latest state of an order item, the customer may cancel an item or submit a refund request. These interactions demonstrate that order processing was implemented as a live business workflow rather than as a static record.

Minor interactions such as login before order access and straightforward navigation to the order pages are better demonstrated in the video instead of with detailed screenshots.

## 5.3 Vendor-Side Operations and Multi-Vendor Support

Another major project outcome is the delivery of a separate vendor-facing operational area. This is the main evidence for Block F because the system is not limited to a single-store catalogue. Instead, different vendors can register, open a shop, manage their own products, maintain shop media, create promotions, and process the order items associated with their own store.

### 5.3.1 Vendor Registration, Shop Identity, and Public Shop Pages

Each vendor can register an account and create a shop with its own name, description, and supporting images. The public shop page presents this information together with the products of that store, allowing customers to browse by vendor rather than only by the global catalogue. This strengthens the platform structure because the system supports both marketplace-wide browsing and shop-specific browsing.

The shop page is a useful project outcome from both a technical and design perspective. Technically, it links a vendor, a store profile, store media, and the related products. From a user perspective, it gives each vendor a recognisable identity within the marketplace and makes the multi-vendor architecture visible to customers.

Suggested figure placement:

- Figure 5.4 Public shop page showing vendor branding, shop gallery, and in-shop product listing

### 5.3.2 Vendor Dashboard and Catalogue Maintenance

The vendor dashboard is the central administration area for maintaining the catalogue. Vendors can add new products, edit existing product information, upload multiple product images, set a primary product image, disable products temporarily, upload shop photos, and review summary statistics such as product counts, sales totals, wishlisted products, and recent search terms.

This is a substantial project outcome because it demonstrates that the system supports ongoing catalogue maintenance rather than only initial data entry. Product records can be updated after creation, media can be changed, and product visibility can be controlled without deleting records. From the perspective of Block B, the multiple-product-photo requirement is handled not only in the storefront display but also in the back-office maintenance tools used by vendors.

The vendor dashboard also provides simple analytics relevant to retail decision-making. These include the most wishlisted products, the most viewed products over the last 30 days based on recorded click history, and recent customer search terms. The combination of wishlist counts, browsing data, and search queries gives vendors a basic but practical picture of customer demand, which supports more informed decisions about pricing, stock management, and promotional timing. The dashboard also supports a product search function that allows vendors to filter their catalogue by name, description, or product ID, which becomes important as the number of listed products grows.

Suggested figure placement:

- Figure 5.5 Vendor dashboard with product table, shop media management, and analytics summaries

### 5.3.3 Vendor Order Processing

On the vendor side, order handling is implemented through a dedicated order management page. Vendors can view the orders that contain their products, inspect customer and shipping information, see each ordered item, and update order-item status through the defined workflow. The system also supports handling customer refund requests from this same operational view.

This outcome is important for Block B because it demonstrates the order-processing workflow in practice. Status updates are not only stored internally but also exposed through an interface that lets vendors move items through the order lifecycle. At the same time, customers are informed through notifications and can see the resulting status changes in their own order pages.

For Block F, the vendor order view shows the separation of responsibility among vendors. Each vendor works on the products belonging to that vendor's own store, rather than managing the complete marketplace catalogue. This separation is a key part of the system architecture and one of the project's main non-trivial achievements.

Suggested figure placement:

- Figure 5.6 Vendor order-processing page with status updates and refund response controls

## 5.4 User-Generated Content and Customer Engagement

### 5.4.1 Reviews, Ratings, and Review Photos

Block T was implemented through a customer review system attached to purchased products. Customers who have previously bought a product can submit a rating and an optional written comment. The system prevents unsupported reviews by checking purchase history before allowing review submission, which makes the review content more reliable and more meaningful for later shoppers.

The review function goes beyond a minimal rating form because it also supports photo upload. Review photos are processed and resized so that they can be displayed effectively inside the product page. This improves the quality of user-generated content and gives future customers stronger visual evidence from actual users rather than from the vendor only.

Customers can also delete their own reviews, which gives them continued control over the content they have contributed. The review photo file is removed from storage when a review is deleted, so the system manages the lifecycle of user-uploaded media rather than accumulating orphaned files.

From a project-outcome perspective, this feature is significant because it introduces community-generated trust signals into the shopping process. Ratings, comments, and review images enrich the product page and help customers judge the quality and appeal of a record before purchase.

Suggested figure placement:

- Figure 5.7 Review section with star ratings, customer comments, and review photo example

### 5.4.2 Wishlist and Promotional Pricing Strategy

Block U was implemented as both a customer convenience feature and a vendor sales mechanism. Customers can add products to a wishlist for future consideration, remove them later, and revisit the saved list from a dedicated wishlist page. The system stores pricing information connected to the wishlist so that current discounts can be compared with the earlier saved state.

The wishlist page also applies a deliberate sorting strategy: products with currently active promotions are displayed first, ranked by discount rate in descending order. This means that when a customer opens their wishlist, items that are on sale are immediately visible at the top of the list rather than buried among non-discounted products. This is a small but commercially meaningful design choice because it directs attention toward time-sensitive purchasing opportunities.

This feature becomes more valuable because it is integrated with the promotional pricing subsystem. Vendors can create percentage-based promotions for products with defined start and end dates. The system automatically expires promotions whose end date has passed, so discounted prices do not persist beyond the intended promotional period. When a promotion becomes active, discounted prices are reflected across the storefront, product page, cart, checkout, and wishlist. Vendors can also manually toggle a promotion between active and inactive states, giving them direct control over sale visibility without deleting and recreating the promotion. In addition, the notification system alerts customers when items in their wishlist go on sale. This creates a clear link between customer intent and vendor marketing strategy.

The project therefore achieves more than a simple save-for-later list. It implements a small but meaningful promotional strategy in which wishlist behaviour, current discounts, and customer notifications are connected. This is one of the most commercially oriented outcomes of the project because it shows how user-interest data can support conversion.

Suggested figure placement:

- Figure 5.8 Wishlist page showing saved items and promotional price changes
- Figure 5.9 Vendor promotion management interface

### 5.4.3 Notifications and Search Behaviour Support

To support engagement and UX quality, the system includes an in-application notification mechanism for both customers and vendors. Customers can receive order-status updates, refund responses, and wishlist promotion notices. Vendors can receive new-order alerts and refund-request notifications. This reduces the need for users to repeatedly check multiple pages manually and makes the shopping process feel more responsive.

The system also records customer search queries and surfaces recent search terms in vendor-facing analytics. This complements Block U because it provides vendors with evidence of customer interest and supports better timing or selection of promotions.

### 5.4.4 Click History and Browsing Behaviour

The system tracks product views for logged-in customers through a click history mechanism. Each time a customer opens a product detail page, the visit is recorded with the product and timestamp. Customers can access a dedicated browsing history page that shows the products they have recently viewed, deduplicated so that each product appears only once with the most recent visit date.

This feature serves two purposes. For the customer, it functions as a convenient way to find products they viewed earlier but did not add to the cart or wishlist at the time. For vendors, the aggregated click history data feeds the most-viewed-products analytics on the vendor dashboard, where the top products by view count over the last 30 days are displayed. This creates a feedback loop where customer browsing behaviour directly informs vendor decision-making, connecting the storefront experience to the back-office analytics without requiring any manual reporting.

## 5.5 User Experience Design Outcome

Block X was addressed throughout the system rather than in a single isolated page. The UX work focused on making the application understandable, efficient, and visually consistent for both customers and vendors.

First, the interface uses a responsive layout so that major pages work across desktop and smaller mobile screens. Product browsing, navigation, forms, and action buttons adapt to available screen width. The product list changes its browsing behaviour to remain usable on smaller devices, while the vendor interface keeps denser information visible on larger screens where management work is more likely to occur.

Second, the system uses consistent visual patterns across the application. Navigation is kept stable through a shared base layout. Alerts, buttons, cards, badges, and tables follow a consistent style, which reduces the learning cost when users move from browsing to ordering or from the storefront to profile and wishlist pages.

Third, the design emphasises transaction clarity. Status labels are colour-coded, order information is grouped logically, and vendor dashboards present product and order information in a way that supports quick scanning. Notification badges and dropdowns help users notice updates without leaving the current task. These decisions are important because UX quality in this project is not only about appearance; it is also about reducing friction in real shopping and administration workflows.

Finally, the project outcome shows that UX considerations were applied to the interaction model itself. Customer browsing, vendor management, refund handling, media upload, and wishlist management all include feedback messages, clear affordances, and page structures that guide the user toward the next meaningful action.

Suggested figure placement:

- Figure 5.10 Mobile and desktop comparison of the storefront layout
- Figure 5.11 Notification dropdown and order-status display examples

## 5.6 Overall Assessment of the Project Outcome

Overall, the project outcome is a coherent online shopping system that integrates the selected specification blocks into one working application. Block A provides the transactional foundation of browsing, cart, checkout, and order history. Block B extends the realism of the platform through multiple product photos and an operational order-status workflow. Block F transforms the system from a single-store shop into a marketplace-style platform with separate vendors and shop identities. Blocks T and U enrich the commercial value of the system through customer reviews, review photos, wishlist support, promotional pricing, notifications, and search-based engagement features. Block X ties these functions together through responsive and consistent user experience design.

The main value of the developed system lies in the fact that these features were not implemented as disconnected demonstrations. They were combined into realistic customer and vendor workflows, which makes the final product a meaningful outcome of the project rather than a collection of isolated pages. For the remaining simple interactions and short operational demonstrations, the accompanying video can present them more efficiently than a large number of screenshots in the report.
