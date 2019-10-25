# Engineered Features

These are all the features in the third notebook:

Type | Name | Explanation | Data Type
---- | ---- | ----------- | ---------
Basic | Price | price of ad item | int
Basic | title_length | # of characters in Ad Title | int
Basic | common_params_cnt | # of matching 'parameters' in Search Query & Ad | int
Basic | Position | position of ad in Search Results | category 
Basic | CategoryID_a | Category ID for Ad | category
Basic | IsUserLoggedOn | whether User was logged in to account at time of impression | binary category
Basic | blank_query | whether the Search Query was blank | binary category
Basic | categories_match | whether the Search Category ID matches the Ad Category ID | binary category
User| user_total_searches | total # of searches for user | int
User| user_cat_diversity | # of unique search categories queried by user | int
User| user_total_impressions | total # of impressions seen by user | int
User| user_total_clicks | total # of clicks by user | int
User| hist_user_total_visits | # of landing page visits by user prior to last 7 searches | int
User| user_HCTR | user's total clicks / user's total impressions | float
Search Category | cat_total_searches | total # of searches for Search Category | int
Search Category | cat_mean_price | avg price for item in Search Category | float
Search Category | cat_total_clicks | total # of clicks for Search Category | int
Search Category | cat_total_impressions | total # of impressions for Search Category | int
Search Category | cat_HCTR | Search Cat. total clicks / Search Cat. total clicks | float
Ad | ad_total_impressions | total # of impressions for ad | int
Ad | ad_total_clicks | total # of clicks for ad | int
Ad | ad_HCTR | total # of clicks for ad / total # of impressions for ad | float
User-Ad | times_user_has_seen_ad | # of times user has seen ad | int

*Note: Aside from the 'Basic' features that are inherently tied to the impression itself,
all the other aggregate features are careful to keep the correct order of the time-series 
in this dataset.*  For instance, 'user_total_searches' denotes all the User's searches *up until* the 
impression being trained on or tested on.  

In the case of the **'Search Category' and 'Ad' features**, those **are 1-day lagged aggregate 
features**.  That is, if an impression being trained on occurred on 5/18, then the
'Search Category' and 'Ad' features are totals and derivations up through the end of 5/17.

Many of these features are correlated, as well, so you get slightly better performance 
if you drop some of the redundant ones, e.g. HCTR is the interaction between total clicks
and total impressions, so the parent features can be dropped.