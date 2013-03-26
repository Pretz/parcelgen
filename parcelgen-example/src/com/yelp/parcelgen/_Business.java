package com.yelp.parcelgen;

import android.net.Uri;
import android.os.Parcel;
import android.os.Parcelable;
import java.io.Serializable;
import org.json.JSONException;
import org.json.JSONObject;

/** Automatically generated Parcelable implementation for _Business.
 *    DO NOT MODIFY THIS FILE MANUALLY! IT WILL BE OVERWRITTEN THE NEXT TIME
 *    _Business's PARCELABLE DESCRIPTION IS CHANGED.
 */
/* package */ abstract class _Business extends Object implements Parcelable, Serializable {

	protected Location mLocation;
	protected String mId;
	protected String mName;
	protected String mImageUrl;
	protected String mPhone;
	protected String mDisplayPhone;
	protected String mRatingImageUrl;
	protected String mRatingImageUrlSmall;
	protected String mSnippetText;
	protected String mSnippetImageUrl;
	protected Uri mUri;
	protected Uri mMobileUri;
	protected double mDistance;
	protected double mRating;
	protected int mReviewCount;

	protected _Business(Location location, String id, String name, String imageUrl, String phone, String displayPhone, String ratingImageUrl, String ratingImageUrlSmall, String snippetText, String snippetImageUrl, Uri uri, Uri mobileUri, double distance, double rating, int reviewCount) {
		this();
		mLocation = location;
		mId = id;
		mName = name;
		mImageUrl = imageUrl;
		mPhone = phone;
		mDisplayPhone = displayPhone;
		mRatingImageUrl = ratingImageUrl;
		mRatingImageUrlSmall = ratingImageUrlSmall;
		mSnippetText = snippetText;
		mSnippetImageUrl = snippetImageUrl;
		mUri = uri;
		mMobileUri = mobileUri;
		mDistance = distance;
		mRating = rating;
		mReviewCount = reviewCount;
	}

	protected _Business() {
		super();
	}

	public Location getLocation() {
		 return mLocation;
	}

	public void setLocation(Location location) {
		 this.mLocation = location;
	}

	public String getId() {
		 return mId;
	}

	public void setId(String id) {
		 this.mId = id;
	}

	public String getName() {
		 return mName;
	}

	public void setName(String name) {
		 this.mName = name;
	}

	public String getImageUrl() {
		 return mImageUrl;
	}

	public void setImageUrl(String imageUrl) {
		 this.mImageUrl = imageUrl;
	}

	public String getPhone() {
		 return mPhone;
	}

	public void setPhone(String phone) {
		 this.mPhone = phone;
	}

	public String getDisplayPhone() {
		 return mDisplayPhone;
	}

	public void setDisplayPhone(String displayPhone) {
		 this.mDisplayPhone = displayPhone;
	}

	public String getRatingImageUrl() {
		 return mRatingImageUrl;
	}

	public void setRatingImageUrl(String ratingImageUrl) {
		 this.mRatingImageUrl = ratingImageUrl;
	}

	public String getRatingImageUrlSmall() {
		 return mRatingImageUrlSmall;
	}

	public void setRatingImageUrlSmall(String ratingImageUrlSmall) {
		 this.mRatingImageUrlSmall = ratingImageUrlSmall;
	}

	public String getSnippetText() {
		 return mSnippetText;
	}

	public void setSnippetText(String snippetText) {
		 this.mSnippetText = snippetText;
	}

	public String getSnippetImageUrl() {
		 return mSnippetImageUrl;
	}

	public void setSnippetImageUrl(String snippetImageUrl) {
		 this.mSnippetImageUrl = snippetImageUrl;
	}

	public Uri getUri() {
		 return mUri;
	}

	public void setUri(Uri uri) {
		 this.mUri = uri;
	}

	public Uri getMobileUri() {
		 return mMobileUri;
	}

	public void setMobileUri(Uri mobileUri) {
		 this.mMobileUri = mobileUri;
	}

	public double getDistance() {
		 return mDistance;
	}

	public void setDistance(double distance) {
		 this.mDistance = distance;
	}

	public double getRating() {
		 return mRating;
	}

	public void setRating(double rating) {
		 this.mRating = rating;
	}

	public int getReviewCount() {
		 return mReviewCount;
	}

	public void setReviewCount(int reviewCount) {
		 this.mReviewCount = reviewCount;
	}


	public int describeContents() {
		return 0;
	}

	public void writeToParcel(Parcel parcel, int flags) {
		parcel.writeParcelable(mLocation, 0);
		parcel.writeValue(mId);
		parcel.writeValue(mName);
		parcel.writeValue(mImageUrl);
		parcel.writeValue(mPhone);
		parcel.writeValue(mDisplayPhone);
		parcel.writeValue(mRatingImageUrl);
		parcel.writeValue(mRatingImageUrlSmall);
		parcel.writeValue(mSnippetText);
		parcel.writeValue(mSnippetImageUrl);
		parcel.writeParcelable(mUri, 0);
		parcel.writeParcelable(mMobileUri, 0);
		parcel.writeDouble(mDistance);
		parcel.writeDouble(mRating);
		parcel.writeInt(mReviewCount);
	}

	public void readFromParcel(Parcel source) {
		mLocation = source.readParcelable(Location.class.getClassLoader());
		mId = (String) source.readValue(String.class.getClassLoader());
		mName = (String) source.readValue(String.class.getClassLoader());
		mImageUrl = (String) source.readValue(String.class.getClassLoader());
		mPhone = (String) source.readValue(String.class.getClassLoader());
		mDisplayPhone = (String) source.readValue(String.class.getClassLoader());
		mRatingImageUrl = (String) source.readValue(String.class.getClassLoader());
		mRatingImageUrlSmall = (String) source.readValue(String.class.getClassLoader());
		mSnippetText = (String) source.readValue(String.class.getClassLoader());
		mSnippetImageUrl = (String) source.readValue(String.class.getClassLoader());
		mUri = source.readParcelable(Uri.class.getClassLoader());
		mMobileUri = source.readParcelable(Uri.class.getClassLoader());
		mDistance = source.readDouble();
		mRating = source.readDouble();
		mReviewCount = source.readInt();
	}

	public void readFromJson(JSONObject json) throws JSONException {
		if (!json.isNull("location")) {
			mLocation = Location.CREATOR.parse(json.getJSONObject("location"));
		}
		if (!json.isNull("id")) {
			mId = json.optString("id");
		}
		if (!json.isNull("name")) {
			mName = json.optString("name");
		}
		if (!json.isNull("image_url")) {
			mImageUrl = json.optString("image_url");
		}
		if (!json.isNull("phone")) {
			mPhone = json.optString("phone");
		}
		if (!json.isNull("display_phone")) {
			mDisplayPhone = json.optString("display_phone");
		}
		if (!json.isNull("rating_img_url")) {
			mRatingImageUrl = json.optString("rating_img_url");
		}
		if (!json.isNull("rating_img_url_small")) {
			mRatingImageUrlSmall = json.optString("rating_img_url_small");
		}
		if (!json.isNull("snippet_text")) {
			mSnippetText = json.optString("snippet_text");
		}
		if (!json.isNull("snippet_image_url")) {
			mSnippetImageUrl = json.optString("snippet_image_url");
		}
		if (!json.isNull("url")) {
			mUri = Uri.parse(json.getString("url"));
		}
		if (!json.isNull("mobile_url")) {
			mMobileUri = Uri.parse(json.getString("mobile_url"));
		}
		mDistance = json.optDouble("distance");
		mRating = json.optDouble("rating");
		mReviewCount = json.optInt("review_count");
	}

}
