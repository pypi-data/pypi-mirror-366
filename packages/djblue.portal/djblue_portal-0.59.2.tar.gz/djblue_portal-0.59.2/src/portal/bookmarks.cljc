(ns portal.bookmarks
  (:require [portal.api :as p]))

(defonce bookmarks (atom []))

(defn open
  "Open bookmark vector."
  {:command true}
  []
  (p/inspect bookmarks {:title "portal-bookmarks"}))

(defn get-bookmark [id] (get @bookmarks id ::not-found))

(defn clear
  "Clear bookmarks."
  []
  (swap! bookmarks empty))

(defn put
  "Add to bookmarks."
  {:command true}
  [value]
  (or (first
       (keep-indexed
        (fn [index v]
          (when (= v value) index))
        @bookmarks))
      (dec (count (swap! bookmarks conj value)))))

(defn copy
  "Copy bookmark pointer."
  {:command true}
  [value]
  (pr-str (list `get-bookmark (put value))))

(p/register! #'clear)
(p/register! #'copy)
(p/register! #'open)
(p/register! #'put)