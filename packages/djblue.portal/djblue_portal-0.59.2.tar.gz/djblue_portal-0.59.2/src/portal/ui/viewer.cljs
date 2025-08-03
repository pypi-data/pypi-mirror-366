(ns ^:no-doc portal.ui.viewer
  (:refer-clojure :exclude [#_#_coll? map? char?])
  (:require [clojure.set :as set]
            [portal.runtime.cson :as cson]
            [portal.ui.api :as api]
            [reagent.core :as r])
  (:import
   [goog.math Long]))

(defn viewers-by-name [viewers]
  (into {} (map (juxt :name identity) viewers)))

(defn url? [value] (instance? js/URL value))
(defn bin? [value] (instance? js/Uint8Array value))
(defn bigint? [value] (= (type value) js/BigInt))
(defn error? [value] (instance? js/Error value))
(defn char? [value] (instance? cson/Character value))
(defn ratio? [value] (instance? cson/Ratio value))

(defn- long? [value] (instance? Long value))

(defn- scalar? [value]
  (or (nil? value)
      (boolean? value)
      (number? value)
      (keyword? value)
      (symbol? value)
      (string? value)
      (long? value)
      (url? value)
      (bigint? value)
      (char? value)
      (ratio? value)
      (inst? value)
      (uuid? value)))

(defn- scalar-seq? [value]
  (and (coll? value)
       (seq value)
       (every? scalar? value)))

(defn- get-compatible-viewers-1 [viewers {:keys [collection key value] :as context}]
  ;; (when-let [v (get-in (meta collection) [:portal.viewer/for])]
  ;;   (tap> {:meta v :value value :collection collection :key key}))
  (let [by-name        (viewers-by-name viewers)
        default-viewer (get by-name
                            (or (get-in (meta collection) [:portal.viewer/for key])
                                (get-in (meta context) [:props :portal.viewer/default])
                                (:portal.viewer/default (meta value))
                                (:portal.viewer/default context)
                                (when (scalar-seq? value)
                                  :portal.viewer/pprint)))
        viewers        (cons default-viewer (remove #(= default-viewer %) viewers))]
    (filter #(when-let [pred (:predicate %)] (pred value)) viewers)))

(defn get-compatible-viewers [viewers contexts]
  (if (nil? contexts)
    (get-compatible-viewers-1 viewers contexts)
    (->> contexts
         (map #(get-compatible-viewers-1 viewers %))
         (map set)
         (apply set/intersection))))

(defn get-location
  "Get a stable location for a given context."
  [context]
  (with-meta
    (select-keys context [:value :stable-path])
    {:context context}))

(defn- get-selected-viewer
  ([state context]
   (get-selected-viewer state context (:value context)))
  ([state context value]
   (get-selected-viewer state context (get-location context) value))
  ([state context location value]
   (when-let [selected-viewer
              (and (= (:value context) value)
                   @(r/cursor state [:selected-viewers location]))]
     (some #(when (= (:name %) selected-viewer) %) @api/viewers))))

(defn- get-compatible-viewer [context value]
  (first (get-compatible-viewers-1 @api/viewers (assoc context :value value))))

(defn get-viewer
  ([state context]
   (get-viewer state context (:value context)))
  ([state context value]
   (or (get-selected-viewer state context value)
       (get-compatible-viewer context value))))
