"use client";

import { ReactNode, useState, createContext } from "react";
import Toaster from "./Toaster";
import Toast from "./Toast";

type ToastMetadata = {
  id: string;
  level: "info" | "error";
  message: string;
  lifespan: number | "inf";
};

type EnqueueToastProps = Pick<ToastMetadata, "level" | "message"> & {
  lifespan?: number | "inf";
};

type ToastQueueContext = {
  enqueueToast: (props: EnqueueToastProps) => string | null;
};

export const ToastQueueContext = createContext({} as ToastQueueContext);
const { Provider } = ToastQueueContext;

const TOAST_LIMIT = 5;
const TOAST_LIFESPAN = 5000;

type ToastQueueProviderProps = {
  children: ReactNode;
};

export default function ToastQueueProvider(props: ToastQueueProviderProps) {
  const [queue, setQueue] = useState<ToastMetadata[]>([]);

  function enqueueToast(props: EnqueueToastProps) {
    if (queue.length >= TOAST_LIMIT) {
      return null;
    }

    const id = `toast-${Date.now()}`;
    const { level, message, lifespan } = props;
    const toast = {
      id,
      level,
      message,
      lifespan: lifespan ?? TOAST_LIFESPAN,
    };

    setQueue((existing) => [...existing, toast]);
    return id;
  }

  function removeToast(id: string) {
    setQueue((existing) => [...existing.filter((toast) => toast.id !== id)]);
  }

  return (
    <Provider value={{ enqueueToast }}>
      <Toaster>
        {queue.map(({ id, level, message, lifespan }) => (
          <Toast
            key={id}
            remove={() => removeToast(id)}
            level={level}
            message={message}
            lifespan={lifespan}
          />
        ))}
      </Toaster>
      {props.children}
    </Provider>
  );
}
