package com.yelp.parcelgen;

import android.os.Parcel;
import android.os.Parcelable;
import com.yelp.parcelgen.JsonUtil;
import java.util.List;
import org.json.JSONException;
import org.json.JSONObject;

/** Automatically generated Parcelable implementation for _Location.
 *    DO NOT MODIFY THIS FILE MANUALLY! IT WILL BE OVERWRITTEN THE NEXT TIME
 *    _Location's PARCELABLE DESCRIPTION IS CHANGED.
 */
/* package */ abstract class _Location extends Object implements Parcelable {

	protected List<String> mAddress;
	protected List<String> mDisplayAddress;
	protected List<String> mNeighborhoods;
	protected String mCity;
	protected String mStateCode;
	protected String mPostalCode;
	protected String mCountryCode;
	protected String mCrossStreets;
	protected double mLatitude;
	protected double mLongitude;
	protected double mGeoAccuracy;

	protected _Location(List<String> address, List<String> displayAddress, List<String> neighborhoods, String city, String stateCode, String postalCode, String countryCode, String crossStreets, double latitude, double longitude, double geoAccuracy) {
		this();
		mAddress = address;
		mDisplayAddress = displayAddress;
		mNeighborhoods = neighborhoods;
		mCity = city;
		mStateCode = stateCode;
		mPostalCode = postalCode;
		mCountryCode = countryCode;
		mCrossStreets = crossStreets;
		mLatitude = latitude;
		mLongitude = longitude;
		mGeoAccuracy = geoAccuracy;
	}

	protected _Location() {
		super();
	}

	public List<String> getAddress() {
		 return mAddress;
	}

	public void setAddress(List<String> address) {
		 this.mAddress = address;
	}

	public List<String> getDisplayAddress() {
		 return mDisplayAddress;
	}

	public void setDisplayAddress(List<String> displayAddress) {
		 this.mDisplayAddress = displayAddress;
	}

	public List<String> getNeighborhoods() {
		 return mNeighborhoods;
	}

	public void setNeighborhoods(List<String> neighborhoods) {
		 this.mNeighborhoods = neighborhoods;
	}

	public String getCity() {
		 return mCity;
	}

	public void setCity(String city) {
		 this.mCity = city;
	}

	public String getStateCode() {
		 return mStateCode;
	}

	public void setStateCode(String stateCode) {
		 this.mStateCode = stateCode;
	}

	public String getPostalCode() {
		 return mPostalCode;
	}

	public void setPostalCode(String postalCode) {
		 this.mPostalCode = postalCode;
	}

	public String getCountryCode() {
		 return mCountryCode;
	}

	public void setCountryCode(String countryCode) {
		 this.mCountryCode = countryCode;
	}

	public String getCrossStreets() {
		 return mCrossStreets;
	}

	public void setCrossStreets(String crossStreets) {
		 this.mCrossStreets = crossStreets;
	}

	public double getLatitude() {
		 return mLatitude;
	}

	public void setLatitude(double latitude) {
		 this.mLatitude = latitude;
	}

	public double getLongitude() {
		 return mLongitude;
	}

	public void setLongitude(double longitude) {
		 this.mLongitude = longitude;
	}

	public double getGeoAccuracy() {
		 return mGeoAccuracy;
	}

	public void setGeoAccuracy(double geoAccuracy) {
		 this.mGeoAccuracy = geoAccuracy;
	}


	public int describeContents() {
		return 0;
	}

	public void writeToParcel(Parcel parcel, int flags) {
		parcel.writeStringList(mAddress);
		parcel.writeStringList(mDisplayAddress);
		parcel.writeStringList(mNeighborhoods);
		parcel.writeValue(mCity);
		parcel.writeValue(mStateCode);
		parcel.writeValue(mPostalCode);
		parcel.writeValue(mCountryCode);
		parcel.writeValue(mCrossStreets);
		parcel.writeDouble(mLatitude);
		parcel.writeDouble(mLongitude);
		parcel.writeDouble(mGeoAccuracy);
	}

	public void readFromParcel(Parcel source) {
		mAddress = source.createStringArrayList();
		mDisplayAddress = source.createStringArrayList();
		mNeighborhoods = source.createStringArrayList();
		mCity = (String) source.readValue(String.class.getClassLoader());
		mStateCode = (String) source.readValue(String.class.getClassLoader());
		mPostalCode = (String) source.readValue(String.class.getClassLoader());
		mCountryCode = (String) source.readValue(String.class.getClassLoader());
		mCrossStreets = (String) source.readValue(String.class.getClassLoader());
		mLatitude = source.readDouble();
		mLongitude = source.readDouble();
		mGeoAccuracy = source.readDouble();
	}

	public void readFromJson(JSONObject json) throws JSONException {
		if (!json.isNull("address")) {
			mAddress = JsonUtil.getStringList(json.optJSONArray("address"));
		} else {
			mAddress = java.util.Collections.emptyList();
		}
		if (!json.isNull("display_address")) {
			mDisplayAddress = JsonUtil.getStringList(json.optJSONArray("display_address"));
		} else {
			mDisplayAddress = java.util.Collections.emptyList();
		}
		if (!json.isNull("neighborhoods")) {
			mNeighborhoods = JsonUtil.getStringList(json.optJSONArray("neighborhoods"));
		} else {
			mNeighborhoods = java.util.Collections.emptyList();
		}
		if (!json.isNull("city")) {
			mCity = json.optString("city");
		}
		if (!json.isNull("state_code")) {
			mStateCode = json.optString("state_code");
		}
		if (!json.isNull("postal_code")) {
			mPostalCode = json.optString("postal_code");
		}
		if (!json.isNull("country_code")) {
			mCountryCode = json.optString("country_code");
		}
		if (!json.isNull("cross_streets")) {
			mCrossStreets = json.optString("cross_streets");
		}
		if (!json.isNull("geo_accuracy")) {
			mGeoAccuracy = json.optDouble("geo_accuracy");
		} else {
			mGeoAccuracy = -1;
		}
	}

}
